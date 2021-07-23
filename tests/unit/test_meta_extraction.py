import glob
import os
import pickle
import pytest
import pydicom
import sys

from pathlib import Path, PurePath
from pytest_mock import MockerFixture

niffler_modules_path = Path.cwd() / 'modules'
meta_extraction_path = niffler_modules_path / 'meta-extraction'
sys.path.append(str(meta_extraction_path))
import MetadataExtractor


@pytest.fixture(autouse=True)
def mock_logger(mocker: MockerFixture):
    return mocker.patch('MetadataExtractor.logging')


@pytest.fixture(autouse=True)
def mock_global_config(mocker: MockerFixture):
    STORAGE_FOLDER = pytest.out_dir / 'meta-extraction' / 'storage_folder'
    PICKLE_FOLDER = pytest.out_dir / 'meta-extraction' / 'pickles'
    pytest.create_dirs(STORAGE_FOLDER, PICKLE_FOLDER)
    return mocker.patch.multiple(
        MetadataExtractor,
        STORAGE_FOLDER=str(STORAGE_FOLDER),
        PICKLE_FOLDER=str(PICKLE_FOLDER) + "/"
    )


@pytest.fixture
def features_lists():
    features_lists = list()
    txt_files = glob.glob(
        str(meta_extraction_path / 'conf') + '/*.txt'
    )
    for file in txt_files:
        text_file = open(file, "r")
        feature_list = text_file.read().split('\n')
        del feature_list[-1]
        features_lists.append(feature_list)
    return features_lists


@pytest.fixture
def feature_files():
    feature_files = list()
    txt_files = glob.glob(
        str(meta_extraction_path / 'conf') + '/*.txt'
    )
    for file in txt_files:
        filename, ext = os.path.splitext(file)
        feature_files.append(filename)
    return feature_files


class TestGetTuples:
    test_dcm_file = str(
        pytest.data_dir / 'meta-extraction' / 'input' / 'test-img.dcm')
    test_valid_plan = pydicom.dcmread(test_dcm_file)

    def test_correct_output(self, features_lists):
        for features in features_lists:
            tuple_list = MetadataExtractor.get_tuples(
                self.test_valid_plan, features)
            assert tuple_list[0][0] in features

    def test_correct_output_with_key(self, features_lists):
        key = "rand_key"
        for features in features_lists:
            tuple_list = MetadataExtractor.get_tuples(
                self.test_valid_plan, features, key=key)
            assert tuple_list[0][0].split(key + "_")[-1] in features

    def test_feature_error(self, mock_logger):
        invalid_features = ["some_invalid_feature"]
        MetadataExtractor.get_tuples(self.test_valid_plan, invalid_features)
        MetadataExtractor.logging.debug.assert_called_once()

    # TODO image with feature value of type pydicom.sequence.Sequence
    # TODO minor code coverage


class TestGetDictFields:
    test_dcm_file = str(
        pytest.data_dir / 'meta-extraction' / 'input' / 'test-img.dcm')
    test_valid_plan = pydicom.dcmread(test_dcm_file)

    def test_success(self, features_lists):
        for features in features_lists:
            tuple_list = MetadataExtractor.get_tuples(
                self.test_valid_plan, features)
            dict_fields = MetadataExtractor.get_dict_fields(
                dict(tuple_list), features)
            assert dict_fields[tuple_list[0][0]] == tuple_list[0][1]


class TestMeasureDiskUtil:

    def test_measure_diskutil(self, mock_logger, mock_global_config):
        MetadataExtractor.measure_diskutil()
        MetadataExtractor.logging.info.assert_called_once()


class TestUpdatePickle:

    def setup_method(self):
        self.processed_series_but_yet_to_delete = []
        self.processed_and_deleted_series = []

    def test_update_success(self, mocker, mock_logger, mock_global_config):
        mocker.patch.multiple(
            MetadataExtractor,
            processed_series_but_yet_to_delete=self.processed_series_but_yet_to_delete,
            processed_and_deleted_series=self.processed_and_deleted_series,
        )
        # Function Completes write without error
        MetadataExtractor.update_pickle()
        MetadataExtractor.logging.debug.assert_called_once_with(
            'dumping complete')


class TestClearStorage:

    def setup_method(self):
        self.processed_and_deleted_series = []
        self.processed_series_but_yet_to_delete = ['yet_to_delete']

    @pytest.fixture(autouse=True)
    def mock_series(self, mocker: MockerFixture):
        return mocker.patch.multiple(
            MetadataExtractor,
            processed_series_but_yet_to_delete=self.processed_series_but_yet_to_delete,
            processed_and_deleted_series=self.processed_and_deleted_series,
        )

    @pytest.fixture(autouse=True)
    def mock_shutil(self, mocker: MockerFixture):
        return mocker.patch('MetadataExtractor.shutil')

    def test_file_not_found_error(self, mock_shutil):

        mock_shutil.rmtree.side_effect = FileNotFoundError

        MetadataExtractor.clear_storage()
        MetadataExtractor.logging.debug.assert_any_call(
            'The series of id %s was not found. Hence, not deleted in this iteration. Probably it was already deleted in a previous iteration without being tracked or by an external process',
            self.processed_series_but_yet_to_delete[0]
        )

    def test_conn_reset_error(self, mock_shutil):

        mock_shutil.rmtree.side_effect = ConnectionResetError

        MetadataExtractor.clear_storage()
        MetadataExtractor.logging.debug.assert_any_call(
            'The connection was reset during the deletion')

    def test_os_error(self, mock_shutil):

        mock_shutil.rmtree.side_effect = OSError

        MetadataExtractor.clear_storage()
        MetadataExtractor.logging.debug.assert_any_call(
            'New images arriving for the series. Therefore, do not delete the series: %s',
            self.processed_series_but_yet_to_delete[0]
        )

    def test_success(self):
        MetadataExtractor.clear_storage()
        MetadataExtractor.logging.debug.assert_any_call(
            'Deleted: %s %s %s %s', str(1),
            ' out of ',
            str(len(self.processed_series_but_yet_to_delete)),
            ' remaining extraction completed series.'
        )


class TestRunThreaded:

    def test_thread_start_success(self, mocker):
        stub = mocker.stub(name='job_func_stub')
        MetadataExtractor.run_threaded(stub)
        stub.assert_called_once()

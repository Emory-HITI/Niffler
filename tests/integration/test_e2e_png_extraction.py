import os
import glob
import pytest
import shutil
import sys
import time
from pathlib import Path, PurePath
from pytest_mock import MockerFixture

# Import Niffler Module
niffler_modules_path = Path.cwd() / 'modules'
sys.path.append(str(niffler_modules_path / 'png-extraction'))
import ImageExtractor


@pytest.fixture
def mock_logger(mocker: MockerFixture):
    """
    Mock module logging
    """
    return mocker.patch('ImageExtractor.logging')


def create_out_dir_structure(out_dir: PurePath):
    """
    Creates directory structure for cold-extraction output
    """
    pytest.create_dirs(*[
        out_dir / 'extracted-images',
        out_dir / 'failed-dicom/1',
        out_dir / 'failed-dicom/2',
        out_dir / 'failed-dicom/3',
        out_dir / 'failed-dicom/4',
        out_dir / 'maps',
        out_dir / 'meta'
    ])
    return out_dir


class TestExecute:
    """
    Tests for ImageExtractor.execute
    """

    def generate_kwargs(self, out_dir: PurePath, **kwargs):
        """
        Generates kwargs for ImageExtractor.execute
        """
        kwargs_dict = {
            'pickle_file': str(out_dir / 'ImageExtractor.pickle'),
            'dicom_home': str(pytest.data_dir / 'png-extraction' / 'input'),
            'output_directory': str(out_dir),
            'print_images': True,
            'print_only_common_headers': "True",
            'depth': 0,
            'processes': 0,
            'flattened_to_level': 'study',
            'email': 'test@test.test',
            'send_email': False,
            'no_splits': 1,
            'is16Bit': "True",
            'png_destination': str(out_dir / 'extracted-images') + '/',
            'failed': str(out_dir / 'failed-dicom') + '/',
            'maps_directory': str(out_dir / 'maps') + '/',
            'meta_directory': str(out_dir / 'meta') + '/',
            'LOG_FILENAME': str(out_dir / 'ImageExtractor.out'),
            'metadata_col_freq_threshold': 0.1,
            't_start': time.time(),
            'SpecificHeadersOnly': False,
            'PublicHeadersOnly' : True
        }
        kwargs_dict.update(**kwargs)
        return kwargs_dict

    def setup_method(self):
        """
        Setup for tests
        """
        self.out_dir = pytest.out_dir / 'png-extraction/outputs/TestExecute'
        self.out_dirs_test_success = create_out_dir_structure(
            self.out_dir / 'test_success'
        )
        self.out_no_dicoms = create_out_dir_structure(
            self.out_dir / 'test_no_dicoms'
        )

    def teardown_method(self):
        """
        Cleanup after tests
        """
        shutil.rmtree(self.out_dir)

    def test_success(self, mock_logger):
        """
        ImageExtractor.execute function executes successfully
        Checks content of output dir
        """
        execute_kwargs = self.generate_kwargs(
            out_dir=self.out_dirs_test_success
        )
        ImageExtractor.execute(**execute_kwargs)
        assert len(
            glob.glob(
                f"{execute_kwargs['png_destination']}**/*.png",
                recursive=True
            )
        ) != 0

    def test_no_dicoms(self, mock_logger):
        """
        ImageExtractor.execute function executes
        Checks if script exited using SystemExit
        """
        execute_kwargs = self.generate_kwargs(
            out_dir=self.out_no_dicoms,
            dicom_home=str(
                pytest.data_dir / 'png-extraction' / 'no_input_files')
        )

        ImageExtractor.logging.basicConfig(
            filename=execute_kwargs['LOG_FILENAME'], level=ImageExtractor.logging.DEBUG)

        with pytest.raises(SystemExit):
            ImageExtractor.execute(**execute_kwargs)


class TestImageExtractorModule:
    """
    Tests for ImageExtractor.initialize_config_and_execute
    """

    def generate_config(self, **kwargs):
        """
        Generates kwargs for ImageExtractor.initialize_config_and_execute
        """
        config = {
            "DICOMHome": str(pytest.data_dir / 'png-extraction' / 'input'),
            "OutputDirectory": str(self.default_out_dir),
            "Depth": 0,
            "SplitIntoChunks": 1,
            "PrintImages": True,
            "CommonHeadersOnly": False,
            "UseProcesses": 0,
            "FlattenedToLevel": "patient",
            "is16Bit": True,
            "SendEmail": False,
            "YourEmail": "test@test.test",
            'SpecificHeadersOnly' : False,
            'PublicHeadersOnly': True
        }
        config.update(**kwargs)
        return config

    def setup_method(self):
        """
        Setup for tests
        """
        self.default_out_dir = pytest.out_dir / \
            'png-extraction/outputs-integration/TestImageExtractorModule'

    def teardown_method(self):
        """
        Cleanup after tests
        """
        shutil.rmtree(self.default_out_dir)

    def test_main(self):
        """
        ImageExtractor.initialize_config_and_execute function executes successfully
        Checks content of output dir
        """
        config = self.generate_config()
        ImageExtractor.initialize_config_and_execute(config)
        assert len(
            glob.glob(
                f"{config['OutputDirectory']}/**/*.png",
                recursive=True
            )
        ) != 0

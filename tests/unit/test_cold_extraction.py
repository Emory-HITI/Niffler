import os
import sys
from charset_normalizer import logging
import pytest
import pdb

from io import StringIO
from pathlib import Path
from pytest_mock import MockerFixture

niffler_modules_path = Path.cwd() / 'modules'
cold_extraction_path = niffler_modules_path / 'cold-extraction'
sys.path.append(str(cold_extraction_path))
import ColdDataRetriever as CDR


@pytest.fixture(autouse=True)
def mock_libs(mocker: MockerFixture):
    """
    Mocking ColdDataRetriever module imports
    """
    return [
        mocker.patch('ColdDataRetriever.logging'),
        mocker.patch('ColdDataRetriever.random'),
        mocker.patch('ColdDataRetriever.time'),
        mocker.patch('ColdDataRetriever.os'),
    ]


@pytest.fixture()
def mock_datetime(mocker: MockerFixture):
    """
    Mocking ColdDataRetriever module datetime import
    """
    return mocker.patch('ColdDataRetriever.datetime')


class Config(object):
    """
    Config Object for cold-extraction tests
    """
    input_dir = pytest.data_dir / 'cold-extraction' / 'input'
    storage_folder = pytest.out_dir / 'cold-extraction' / 'storage-folder'

    def __init__(self):
        pytest.create_dirs(
            self.storage_folder,
            self.input_dir
        )


# Initialize config object
test_config = Config()


class TestSetup:
    """
    Initial test setup for all unit test
    """

    def setup_method(self):
        CDR.date_format = "%Y%m%d"

    def test_setup_complete(self):
        assert CDR.date_format != None


class TestUpdatePickle:
    """
    Tests for ColdDataRetriever.update_pickle
    """

    def setup_method(self):
        """
        Setup
        """
        CDR.csv_file = None
        CDR.mod_csv_file = None
        CDR.extracted_ones = None

    def teardown_method(self):
        """
        Cleanup
        """
        CDR.csv_file = None
        CDR.mod_csv_file = None
        CDR.extracted_ones = None

    def test_success(self):
        """
        Test for ColdDataRetriever.update_pickle function.
        Check whether function executes without raising error.
        """
        # CDR.csv_file = str(test_config.input_dir / 'csv_files' / 'tmp.csv')
        CDR.mod_csv_file = str(test_config.input_dir / 'csv_files' / 'tmp_mod.csv')
        CDR.extracted_ones = ['1234,4432']
        CDR.update_pickle()
        CDR.logging.debug.assert_called_once()


class TestRunThreaded:
    """
    Test for ColdDataRetriever.run_threaded
    """

    def test_thread_start_success(self, mocker):
        """
        Checks whether the stub function is called on thread start
        """
        stub = mocker.stub(name='job_func_stub')
        CDR.run_threaded(stub)
        stub.assert_called_once()


class TestSleepForNightlyMode:
    """
    Test for ColdDataRetriever.sleep_for_nightly_mode
    """

    def setup_method(self):
        """
        Setup
        """
        CDR.NIGHTLY_ONLY = True
        CDR.END_HOUR = 8
        CDR.START_HOUR = 24

    def test_success(self, mock_datetime):
        """
        Checks whether infinite the execution reaches the inf while loop
        """
        # To end the loop after 1st iteration
        tmp_date_obj = pytest.Dict2Class({'hour': 12})
        mock_datetime.datetime.now.return_value = tmp_date_obj

        CDR.time.sleep.side_effect = Exception

        with pytest.raises(Exception):
            CDR.sleep_for_nightly_mode()
        CDR.logging.info.assert_called_once()
        CDR.time.sleep.assert_called_once()


class TestConvertToDateFormat:
    """
    Test for ColdDataRetriever.convert_to_date_format
    """

    def test_success(self):
        """
        Checks whether function is executed without exception
        """
        date_str = "20180507"
        ret_date_str = CDR.convert_to_date_format(date_str)
        assert date_str == ret_date_str


class TestCheckKillProcess:
    """
    Tests for ColdDataRetriever.check_kill_process
    """

    def setup_method(self):
        """
        Setup
        """
        CDR.nifflerscp_str = "storescp.*QBNIFFLER"
        CDR.storage_folder = test_config.storage_folder

    def test_kill_success(self):
        """
        Mocks popen and checks whether os.kill is called
        """
        CDR.os.popen.return_value = StringIO(
            "1234 ? R+ 0:00 storescp.*QBNIFFLER\n")
        CDR.os.kill.return_value = None
        CDR.check_kill_process()
        CDR.logging.info.assert_called_once()
        CDR.os.kill.assert_called_once()

    def test_kill_permission_error(self):
        """
        Mocks popen and checks whether os.kill raises PermissionError
        """
        CDR.os.popen.return_value = StringIO(
            "1234 ? R+ 0:00 storescp.*QBNIFFLER\n")
        CDR.os.kill.side_effect = PermissionError

        with pytest.raises(SystemExit):
            CDR.check_kill_process()

        CDR.logging.warning.assert_any_call(
            "From your terminal run the below commands.")


class TestReadCsv:
    """
    Tests for ColdDataRetriever.read_csv
    """

    def reset_cdr_module_state(self):
        """
        Resets module level variables       
        """
        CDR.firsts = []
        CDR.seconds = []
        CDR.thirds = []
        CDR.number_of_query_attributes = 3
        CDR.first_index = 0
        CDR.first_attr = "PatientID"
        CDR.second_index = 1
        CDR.second_attr = "StudyDate"
        CDR.third_index = 2
        CDR.third_attr = "AccessionNumber"

    def setup_method(self):
        """
        Setup
        """
        CDR.mod_csv_file = str(test_config.input_dir /
                           'csv_files' / 'unit_test_read_csv.csv')
        CDR.number_of_query_attributes = 3
        self.reset_cdr_module_state()

    def test_query_attrs_gt_3_or_lt_1(self):
        """
        Tests for execution when number_of_query_attributes > 3 or < 1
        Checks log call based on log content of funtion
        """
        self.reset_cdr_module_state()
        CDR.number_of_query_attributes = 6
        CDR.read_csv()
        CDR.logging.info.assert_any_call(
            'Entered an invalid NumberOfQueryAttributes. Currently supported values, 1, 2, or 3. '
            'Defaulting to 1 for this extraction'
        )
        self.reset_cdr_module_state()
        CDR.number_of_query_attributes = 0
        CDR.read_csv()
        CDR.logging.info.assert_any_call(
            'Entered an invalid NumberOfQueryAttributes. Currently supported values, 1, 2, or 3. '
            'Defaulting to 1 for this extraction'
        )
        self.reset_cdr_module_state()

    def test_first_col_date(self):
        """
        Test when first col is date col in the csv
        Checks read success by asserting value of number of rows read.
        """
        self.reset_cdr_module_state()
        CDR.mod_csv_file = str(test_config.input_dir /
                           'csv_files' / 'unit_test_read_csv_1st_date.csv')
        CDR.first_attr = "StudyDate"
        CDR.second_attr = "PatientID"
        CDR.third_attr = "AccessionNumber"

        CDR.read_csv()
        assert CDR.length == 1
        self.reset_cdr_module_state()

    def test_second_col_date(self):
        """
        Test when second col is date col in the csv
        Checks read success by asserting value of number of rows read.
        """
        self.reset_cdr_module_state()
        CDR.read_csv()
        assert CDR.length == 1
        self.reset_cdr_module_state()

    def test_third_col_date(self):
        """
        Test when third col is date col in the csv
        Checks read success by asserting value of number of rows read.
        """
        self.reset_cdr_module_state()
        CDR.mod_csv_file = str(test_config.input_dir /
                           'csv_files' / 'unit_test_read_csv_3rd_date.csv')

        CDR.first_attr = "PatientID"
        CDR.second_attr = "StudyID"
        CDR.third_attr = "StudyDate"

        CDR.read_csv()
        assert CDR.length == 1
        self.reset_cdr_module_state()

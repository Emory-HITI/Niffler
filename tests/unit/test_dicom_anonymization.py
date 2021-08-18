import sys
import pytest

from pathlib import Path

niffler_modules_path = Path.cwd() / 'modules'
dicom_anon_path = niffler_modules_path / 'dicom-anonymization'
sys.path.append(str(dicom_anon_path))
import DicomAnonymizer as DCMAnon


class Config(object):
    """
    Config Object for dicom-anonymization tests
    """
    input_dir = pytest.data_dir / 'dicom-anonymization' / 'input'

    def __init__(self):
        pytest.create_dirs(
            self.input_dir
        )


# Initialize config object
test_config = Config()


class TestRandomizeID:
    """
    Test for DicomAnonymizer.randomizeID
    """

    def test_success(self):
        """
        Checks whether randomized img id starts with initial part of orig id.
        Refer to DCMAnon.randomizeID code.
        """
        tmp_id = "45365768335.0.7486.131"
        start_str = tmp_id.split(".")[0]
        randId = DCMAnon.randomizeID(tmp_id)
        assert randId.startswith(start_str)


class TestAnonSample:
    """
    Tests for DicomAnonymizer.anonSample
    """

    def test_success_randomize(self):
        """
        Checks whether anonymized img id starts with initial part of orig id.
        Refer to DCMAnon.anonSample code.
        """

        id_type = "some_type"
        tmp_id = "45365768335.0.7486.131"
        start_str = tmp_id.split(".")[0]
        tmp_file = {id_type: pytest.Dict2Class({'value': tmp_id})}
        anon_id = DCMAnon.anonSample(tmp_file, id_type, {})

        assert anon_id.startswith(start_str)

    def test_success_no_randomize(self):
        """
        Checks whether anonymized img id starts with initial part of orig id.
        Test for if conditional
        Refer to DCMAnon.anonSample code.
        """
        id_type = "some_type"
        tmp_id = "45365768335.30.854.131"
        start_str = tmp_id.split(".")[0]
        tmp_file = {id_type: pytest.Dict2Class({'value': tmp_id})}
        anon_id = DCMAnon.anonSample(
            tmp_file, id_type, {tmp_id: '45365768335.0.7486.131'})

        assert anon_id.startswith(start_str)


class TestGetDcmFolders:
    """
    Tests for DicomAnonymizer.get_dcm_folders
    """

    def test_no_files(self):
        """
        Checks whether get_dcm_folders returns 0 folders
        """
        dcm_flds = DCMAnon.get_dcm_folders(
            test_config.input_dir / 'dcm_empty_dir')
        assert len(dcm_flds) == 0

    def test_get_folder(self):
        """
        Checks whether get_dcm_folders returns non 0 length of folders
        """
        dcm_flds = DCMAnon.get_dcm_folders(
            test_config.input_dir / 'dcm_root_dir')
        assert len(dcm_flds) != 0

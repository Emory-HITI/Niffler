import sys
import pytest

from pathlib import Path

niffler_modules_path = Path.cwd() / 'modules'
dicom_anon_path = niffler_modules_path / 'dicom-anonymization'
sys.path.append(str(dicom_anon_path))
import DicomAnonymizer as DCMAnon


class Config(object):
    input_dir = pytest.data_dir / 'dicom-anonymization' / 'input'

    def __init__(self):
        pytest.create_dirs(
            self.input_dir
        )


test_config = Config()


class TestRandomizeID:

    def test_success(self):
        tmp_id = "45365768335.0.7486.131"
        start_str = tmp_id.split(".")[0]
        randId = DCMAnon.randomizeID(tmp_id)
        assert randId.startswith(start_str)


class TestAnonSample:

    def test_success_randomize(self):
        id_type = "some_type"
        tmp_id = "45365768335.0.7486.131"
        start_str = tmp_id.split(".")[0]
        tmp_file = {id_type: pytest.Dict2Class({'value': tmp_id})}
        anon_id = DCMAnon.anonSample(tmp_file, id_type, {})

        assert anon_id.startswith(start_str)

    def test_success_no_randomize(self):
        id_type = "some_type"
        tmp_id = "45365768335.30.854.131"
        start_str = tmp_id.split(".")[0]
        tmp_file = {id_type: pytest.Dict2Class({'value': tmp_id})}
        anon_id = DCMAnon.anonSample(
            tmp_file, id_type, {tmp_id: '45365768335.0.7486.131'})

        assert anon_id.startswith(start_str)


class TestGetDcmFolders:

    def test_no_files(self):
        dcm_flds = DCMAnon.get_dcm_folders(
            test_config.input_dir / 'dcm_empty_dir')
        assert len(dcm_flds) == 0

    def test_get_folder(self):
        dcm_flds = DCMAnon.get_dcm_folders(
            test_config.input_dir / 'dcm_root_dir')
        assert len(dcm_flds) != 0

import os
import sys
import pytest

from pathlib import Path


niffler_modules_path = Path.cwd() / 'modules'
dicom_anon_path = niffler_modules_path / 'dicom-anonymization'
sys.path.append(str(dicom_anon_path))
import DicomAnonymizer as DCMAnon


class Config(object):
    input_dir = pytest.data_dir / 'dicom-anonymization' / 'input'
    output_dir = pytest.out_dir / 'dicom-anonymization' / 'output'

    def __init__(self):
        pytest.create_dirs(
            self.input_dir,
            self.output_dir
        )


test_config = Config()


class TestDcmAnonymize:

    def test_success(self):
        dcm_root_dir = test_config.input_dir / 'dcm_root_dir'
        dcm_output_dir = test_config.output_dir / 'dcm_root_dir_out'
        pytest.create_dirs(dcm_output_dir)
        dcm_folders = DCMAnon.get_dcm_folders(dcm_root_dir)
        with pytest.raises(SystemExit):
            DCMAnon.dcm_anonymize(dcm_folders, dcm_output_dir)

    def test_stop_success(self):
        dcm_root_dir = test_config.input_dir / 'dcm_root_dir'
        dcm_output_dir = test_config.output_dir / 'dcm_root_dir_out'
        pytest.create_dirs(dcm_output_dir)
        dcm_folders = DCMAnon.get_dcm_folders(dcm_root_dir)
        with pytest.raises(SystemExit):
            DCMAnon.dcm_anonymize(dcm_folders, dcm_output_dir, stop=2)

    # TODO: Invalid Dicom file. Empty .txt renamed to .dcm doesn't work.

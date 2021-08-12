import os
import sys
import pytest

from pathlib import Path


niffler_modules_path = Path.cwd() / 'modules'
dicom_anon_path = niffler_modules_path / 'dicom-anonymization'
sys.path.append(str(dicom_anon_path))
import DicomAnonymizer as DCMAnon


class Config(object):
    """
    Config object for DicomAnonymizer tests
    """
    input_dir = pytest.data_dir / 'dicom-anonymization' / 'input'
    output_dir = pytest.out_dir / 'dicom-anonymization' / 'output'

    def __init__(self):
        pytest.create_dirs(
            self.input_dir,
            self.output_dir
        )

# Initialize config object
test_config = Config()


class TestDcmAnonymize:
    """
    Tests for DicomAnonymizer.dcm_anonymize
    """

    def test_success(self):
        """
        Tests Success for dcm_anonymize function with params
        dcm_folder and dcm_output_dir.
        """
        dcm_root_dir = test_config.input_dir / 'dcm_root_dir'
        dcm_output_dir = test_config.output_dir / 'dcm_root_dir_out'
        pytest.create_dirs(dcm_output_dir)
        dcm_folders = DCMAnon.get_dcm_folders(dcm_root_dir)
        try:
            DCMAnon.dcm_anonymize(dcm_folders, dcm_output_dir)
        except SystemExit:
            pass
        except Exception as e:
            pytest.fail(e, pytrace=True)

    def test_stop_success(self):
        """
        Tests Success for dcm_anonymize function with params
        dcm_folder, dcm_output_dir and stop flag.
        """
        dcm_root_dir = test_config.input_dir / 'dcm_root_dir'
        dcm_output_dir = test_config.output_dir / 'dcm_root_dir_out'
        pytest.create_dirs(dcm_output_dir)
        dcm_folders = DCMAnon.get_dcm_folders(dcm_root_dir)
        try:
            DCMAnon.dcm_anonymize(dcm_folders, dcm_output_dir, stop=2)
        except SystemExit:
            pass
        except Exception as e:
            pytest.fail(e, pytrace=True)

    # TODO: Invalid Dicom file. Empty .txt renamed to .dcm doesn't work.

import png
import sys
import pdb
import pytest
import shutil
import numpy as np

from pathlib import Path
from pytest_mock import MockerFixture

# Import Niffler Module
niffler_modules_path = Path.cwd() / 'modules'
sys.path.append(str(niffler_modules_path / 'png-extraction'))
import ImageExtractor

import pydicom
import pandas as pd


@pytest.fixture
def mock_pydicom_config_data_element_callback(mocker: MockerFixture):
    """
    Mocking pydicom config
    """
    return mocker.patch.object(pydicom.config, 'data_element_callback')


@pytest.fixture
def mock_pydicom_config_data_element_callback_kwargs(mocker: MockerFixture):
    """
    Mocking pydicom config
    """
    return mocker.patch.object(pydicom.config, 'data_element_callback_kwargs')


@pytest.fixture
def mock_logger(mocker: MockerFixture):
    """
    Mocking module logging
    """
    return mocker.patch('ImageExtractor.logging')


def is16BitImg(path):
    reader = png.Reader(path)
    pngdata = reader.read_flat()
    img = np.array(pngdata[2]).reshape((pngdata[1], pngdata[0], -1))
    return img.dtype


class TestGetPath:
    """
    Test ImageExtractor.get_path 
    """
    dicom_home = "/mock/path/to/dicom/home"

    def test_get_path_zero_depth(self):
        """
        Test path with depth=0
        """
        depth = 0
        dcm_path = ImageExtractor.get_path(depth, self.dicom_home)
        assert dcm_path == f"{self.dicom_home}/*.dcm"

    def test_get_path_some_depth(self):
        """
        Test path with some depth
        """
        depth = 3
        dcm_path = ImageExtractor.get_path(depth, self.dicom_home)
        assert dcm_path == f"{self.dicom_home}{''.join(['/*']*depth)}/*.dcm"


class TestFixMismatch:
    """
    Test ImageExtractor.fix_mismatch
    """
    with_VRs = ['PN', 'DS', 'IS']

    def test_fix_mismatch(self, mock_pydicom_config_data_element_callback, mock_pydicom_config_data_element_callback_kwargs):
        """
        Checks whether pydicom config is set properly or not
        """
        ImageExtractor.fix_mismatch(with_VRs=self.with_VRs)
        assert pydicom.config.data_element_callback is ImageExtractor.fix_mismatch_callback
        assert pydicom.config.data_element_callback_kwargs['with_VRs'] == self.with_VRs


class TestExtractHeaders:
    """
    Test ImageExtractor.extract_headers
    """
    valid_test_dcm_file = 0, str(
        pytest.data_dir / 'png-extraction' / 'input' / 'test-img.dcm'), True, str(pytest.data_dir / 'png-extraction' / 'output')
    invalid_test_dcm_file = 0, str(
        pytest.data_dir / 'png-extraction' / 'input' / 'no-img.dcm'), True, str(pytest.data_dir / 'png-extraction' / 'output')

    def test_no_image(self):
        """
        Test for invalid image
        """
        headers = ImageExtractor.extract_headers(
            self.invalid_test_dcm_file)
        assert headers['has_pix_array'] is False

    def test_valid_image(self):
        """
        Test for a valid image
        """
        headers = ImageExtractor.extract_headers(self.valid_test_dcm_file)
        assert headers['has_pix_array'] is True

    # TODO large dcm files


class TestGetTuples:
    """
    Tests for ImageExtractor.get_tuples
    """
    test_dcm_file = str(
        pytest.data_dir / 'png-extraction' / 'input' / 'test-img.dcm')
    test_valid_plan = pydicom.dcmread(test_dcm_file, force=True)

    def test_correct_output(self):
        """
        Verifies first key
        """
        first_key = self.test_valid_plan.dir()[0]
        tuple_list = ImageExtractor.get_tuples(self.test_valid_plan,False)
        assert tuple_list[0][0] == first_key

    # TODO hasattr error
    # TODO large dcm files


class TestExtractImages:
    """
    Tests for ImageExtractor.extract_images
    """
    test_dcm_file = str(
        pytest.data_dir / 'png-extraction' / 'input' / 'test-img.dcm')
    invalid_test_dcm_file = str(
        pytest.data_dir / 'png-extraction' / 'input' / 'no-img.dcm')

    def setup_method(self):
        """
        Test Setup
        """
        header_list = [ImageExtractor.extract_headers(
            (0, self.test_dcm_file,True, str(pytest.data_dir / 'png-extraction' / 'output')))]
        self.file_data = pd.DataFrame(header_list)
        self.index = 0
        self.invalid_file_data = pd.DataFrame([
            {
                'some_col_1': 'Dummy Col1 Value',
                'some_col_2': 'Dummy Col2 Value',
                'file': self.invalid_test_dcm_file
            }
        ])
        self.out_dir = pytest.out_dir / 'png-extraction/outputs/TestExtractImages'
        self.png_destination = f"{str(self.out_dir)}/extracted-images/"
        self.failed = f"{str(self.out_dir)}/failed-dicom/"
        pytest.create_dirs(self.out_dir, self.png_destination, self.failed)

    def teardown_method(self):
        """
        Cleanup
        """
        shutil.rmtree(self.out_dir)

    def test_is16bit(self):
        """
        Checks if converted png is 16bit
        """
        flattened_to_level = "patient"
        is16Bit = True
        out_img = ImageExtractor.extract_images(
            self.file_data,
            self.index,
            self.png_destination,
            flattened_to_level,
            self.failed,
            is16Bit
        )
        assert out_img[0].startswith(self.test_dcm_file)
        out_img_file = out_img[0].split(", ")[-1].strip("\n")
        assert is16BitImg(out_img_file) == "uint16"

    def test_not_is16bit(self):
        """
        Checks if converted png is not 16bit
        """
        flattened_to_level = "patient"
        is16Bit = False
        out_img = ImageExtractor.extract_images(
            self.file_data,
            self.index,
            self.png_destination,
            flattened_to_level,
            self.failed,
            is16Bit
        )
        assert out_img[0].startswith(self.test_dcm_file)
        out_img_file = out_img[0].split(", ")[-1].strip("\n")
        assert is16BitImg(out_img_file) != "uint16"

    def test_level_patient(self):
        """
        Check code execution when level set to patient
        """
        flattened_to_level = "patient"
        is16Bit = False
        out_img = ImageExtractor.extract_images(
            self.file_data,
            self.index,
            self.png_destination,
            flattened_to_level,
            self.failed,
            is16Bit
        )
        assert out_img[0].startswith(self.test_dcm_file)

    def test_level_study(self):
        """
        Check code execution when level set to study
        """
        flattened_to_level = "study"
        is16Bit = False
        out_img = ImageExtractor.extract_images(
            self.file_data,
            self.index,
            self.png_destination,
            flattened_to_level,
            self.failed,
            is16Bit
        )
        assert out_img[0].startswith(self.test_dcm_file)

    def test_level_other(self):
        """
        Check code execution when level set to other
        """
        flattened_to_level = "other"
        is16Bit = False
        out_img = ImageExtractor.extract_images(
            self.file_data,
            self.index,
            self.png_destination,
            flattened_to_level,
            self.failed,
            is16Bit
        )
        assert out_img[0].startswith(self.test_dcm_file)

    def test_level_other_no_study_uuid(self):
        """
        Check code execution when no uuid in data for level other
        """
        flattened_to_level = "other"
        is16Bit = False 
        out_img = ImageExtractor.extract_images(
            self.file_data.drop(['StudyInstanceUID'], axis=1),
            self.index,
            self.png_destination,
            flattened_to_level,
            self.failed,
            is16Bit
        )
        assert out_img[0].startswith(self.test_dcm_file)

    def test_level_study_no_study_uuid(self):
        """
        Check code execution when no uuid in data for level study
        """
        flattened_to_level = "study"
        is16Bit = False 
        out_img = ImageExtractor.extract_images(
            self.file_data.drop(['StudyInstanceUID'], axis=1),
            self.index,
            self.png_destination,
            flattened_to_level,
            self.failed,
            is16Bit
        )
        assert out_img[0].startswith(self.test_dcm_file)

    def test_failed_read_attrerr(self):
        """
        Check code execution when read error
        """
        flattened_to_level = "study"
        is16Bit = False 
        out_img = ImageExtractor.extract_images(
            self.invalid_file_data,
            self.index,
            self.png_destination,
            flattened_to_level,
            self.failed,
            is16Bit
        )
        assert out_img[1][0] == self.invalid_test_dcm_file
        # assert that error string is present
        assert out_img[2] is not None

import os
import sys
import logging
import pandas as pd
from HITI_anon_internal.Anon import EmoryAnon

def cold_extraction():
    # Cold Extraction
    logging.info('Starting Cold Extraction')
    COLD_UPLOAD_FOLDER = '../cold-extraction/'
    sys.path.append(COLD_UPLOAD_FOLDER)
    os.chdir(COLD_UPLOAD_FOLDER)
    import ColdDataRetriever
    cold_extraction_values = {}

    NifflerSystem = 'rtniffler.json'
    file_path = '{00100020}/{0020000D}/{0020000E}/{00080018}.dcm'
    date_format = '%Y%m%d'

    cold_extraction_values['NifflerSystem'] = NifflerSystem
    cold_extraction_values['StorageFolder'] = '/home/aredd30/test/cold_extraction/'
    cold_extraction_values['FilePath'] = file_path
    cold_extraction_values['CsvFile'] = '/home/aredd30/test/test_patients.csv'
    cold_extraction_values['FirstAttr'] = 'PatientID'
    cold_extraction_values['FirstIndex'] = 0
    cold_extraction_values['SecondAttr'] = 'AccessionNumber'
    cold_extraction_values['SecondIndex'] = 1
    cold_extraction_values['ThirdAttr'] = 'StudyDate'
    cold_extraction_values['ThirdIndex'] = 2
    cold_extraction_values['NumberOfQueryAttributes'] = 1
    cold_extraction_values['DateFormat'] = date_format
    cold_extraction_values['SendEmail'] = True
    cold_extraction_values['YourEmail'] = 'aredd30@emory.edu'

    ColdDataRetriever.initialize_config_and_execute(cold_extraction_values)
    logging.info('Completed Cold Extraction')

def png_extraction():
    # PNG Extraction
    logging.info('Starting PNG Extraction')
    PNG_UPLOAD_FOLDER = '../png-extraction/'
    sys.path.append(PNG_UPLOAD_FOLDER)
    os.chdir(PNG_UPLOAD_FOLDER)
    import ImageExtractor
    png_extraction_values = {}

    png_extraction_values['DICOMHome'] = '/home/aredd30/test/modality_grouping/CT/'
    png_extraction_values['OutputDirectory'] = '/home/aredd30/test/png_extraction/'
    png_extraction_values['Depth'] = 3
    png_extraction_values['SplitIntoChunks'] = 1
    png_extraction_values['PrintImages'] = True
    png_extraction_values['CommonHeadersOnly'] = True
    png_extraction_values['UseProcesses'] = 0
    png_extraction_values['FlattenedToLevel'] = 'series'
    png_extraction_values['is16Bit'] = True
    png_extraction_values['SendEmail'] = True
    png_extraction_values['YourEmail'] = 'aredd30@emory.edu'

    ImageExtractor.initialize_config_and_execute(png_extraction_values)
    logging.info('Completed PNG Extraction')

def modality_grouping():
    # Modality Grouping
    logging.info('Starting Modality Grouping')
    import ModalityGrouping
    modality_group_values = {}

    modality_group_values['cold_extraction_path'] = '/home/aredd30/test/cold_extraction/'
    modality_group_values['modality_split_path'] = '/home/aredd30/test/modality_grouping/'

    ModalityGrouping.modality_split(modality_group_values['cold_extraction_path'], modality_group_values['modality_split_path'])
    logging.info('Completed Modality Splitting')

def dicom_anonymization():
    # DICOM Anonymization
    logging.info('Starting DICOM Anonymization')
    DICOM_ANON_FOLDER = '../dicom-anonymization/'
    sys.path.append(DICOM_ANON_FOLDER)
    os.chdir(DICOM_ANON_FOLDER)
    import DicomAnonymizer2
    dicom_anonymization_values = {}

    dicom_anonymization_values['dcm_folders'] = '/home/aredd30/test/cold_extraction/'
    dicom_anonymization_values['output_dir'] = '/home/aredd30/test/dicom_anonymization/'

    dcm_folders = DicomAnonymizer2.get_dcm_paths(dicom_anonymization_values['dcm_folders'])
    DicomAnonymizer2.dcm_anonymize(dcm_folders, dicom_anonymization_values['output_dir'])
    logging.info('Completed DICOM Anonymization')

def metadata_anonymization():
    # Metadata Anonymization
    logging.info('Starting Metadata Anonymization')
    import metadata_anonymization
    metadata_anonymization_values = {}

    metadata_anonymization_values['metadata_path'] = '/home/aredd30/test/png_extraction/metadata.csv'
    metadata_anonymization_values['anon_metadata_path'] = '/home/aredd30/test/metadata_anon/metadata.csv'

    Anon = EmoryAnon('/home/Anonymization/PHIAnon/', '/home/Anonymization/textAnon/whitelist.csv')
    Anon.load_recentMasterKey()
    metadata_path = metadata_anonymization_values['metadata_path']
    metadata = pd.read_csv(metadata_path, low_memory=False)
    del_cols = []
    for col in metadata.columns:
        if (metadata[col].isnull().sum() > (0.90*len(metadata))):
            del_cols.append(col)

    metadata = metadata.drop(del_cols, axis=1)
    clean_data = metadata_anonymization.anonymization(metadata, Anon)
    clean_data.to_csv(metadata_anonymization_values['anon_metadata_path'], index=False)
    logging.info('Completed Metadata Anonymization')


if __name__=="__main__":
    log_format = '%(levelname)s %(asctime)s - %(message)s'
    logging.basicConfig(filename='workflow.logs', level=logging.INFO,
                        format=log_format, filemode='w')
    logging = logging.getLogger()

    # cold_extraction()
    modality_grouping()
    png_extraction()
    dicom_anonymization()
    metadata_anonymization()



from HITI_anon_internal.Anon import EmoryAnon
import sys
import pandas as pd

def anonymization(metadata, Anon):
    metadata['AccessionNumber'] = metadata.AccessionNumber.map(str)
    metadata['PatientID'] = metadata.PatientID.map(int)
    metadata['StudyDate_modified'] = pd.to_datetime(metadata['StudyDate'], format='%Y%m%d')

    mask = metadata.AccessionNumber.str.len()==16
    metadata = metadata.loc[mask]
    metadata.reset_index(inplace=True, drop=True)

    metadata['StudyDate'] = metadata.StudyDate.astype(str)
    metadata['StudyDate_formatted'] = (metadata.StudyDate.str.slice(0,4))+'-'+(metadata.StudyDate.str.slice(4,6))+'-'+(metadata.StudyDate.str.slice(6,8))

    metadata = Anon.col_norm(metadata)
    metadata['empi_anon'] = Anon.IDanon(metadata['PatientID'], data_type='empi')
    metadata['acc_anon'] = Anon.IDanon(metadata['AccessionNumber'], data_type='rad_acc')
    metadata['study_date_anon'] = Anon.TScol(metadata['PatientID'], metadata['StudyDate_modified'])
    metadata.to_csv('metadata_orig_and_anon.csv')
    cols_to_drop=['PatientID',
                'AccessionNumber',
                'StudyDate_modified',
                'InstitutionAddress',
                'InstitutionName',
                'OperatorsName',
                'OtherPatientIDs',
                'PatientAddress',
                'PatientBirthDate',
                'PatientName',
                'ReferringPhysicianName',
                'StationName',
                'ContentDate',
                'DeviceSerialNumber',
                'InstitutionalDepartmentName',
                'SeriesDate',
                'AcquisitionDate',
                'DateOfLastDetectorCalibration',
                'DetectorID',
                'PerformedProcedureStepID',
                'PerformedProcedureStepStartDate',
                'RequestingPhysician',        
                'SOPClassUID',
                'SOPInstanceUID',
                'SeriesInstanceUID',
                'StudyInstanceUID',
                'FrameOfReferenceUID',
                'InstanceCreatorUID',
                'IrradiationEventUID',
                'file',
                'AcquisitionDateTime',
                'DateOfSecondaryCapture',
                'EthnicGroup',
                'EthnicGroup',
                'InstanceCreationDate',
                'InstanceCreationTime',
                'InstanceNumber',
                'IssuerOfPatientID',
                'PatientBirthTime',
                'PatientComments',
                'PatientSex',
                'PerformedProcedureStepStartTime',
                'StudyID',
                'StudyTime',
                'TimeOfSecondaryCapture']

    finals_cols_to_drop = []
    for col in cols_to_drop:
        if col in metadata:
            finals_cols_to_drop.append(col)

    clean_data = metadata.drop(finals_cols_to_drop, axis=1)
    Anon.save_keys()
    return (clean_data)


if __name__ == "__main__":

    Anon = EmoryAnon('/home/Anonymization/PHIAnon/', '/home/Anonymization/textAnon/whitelist.csv')
    Anon.load_recentMasterKey()

    metadata_path = sys.argv[1]
    metadata = pd.read_csv(metadata_path, low_memory=False)
    del_cols = []
    for col in metadata.columns:
        if (metadata[col].isnull().sum() > (0.90*len(metadata))):
            del_cols.append(col)    
    
    clean_data = anonymization(metadata, Anon)
    clean_data.to_csv(sys.argv[2], index=False)

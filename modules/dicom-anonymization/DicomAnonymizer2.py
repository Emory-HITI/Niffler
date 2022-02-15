import os
import sys
import pydicom
import random
import glob
import pathlib
import pickle
import string
import random 

def get_dcm_paths(dcm_root_dir):
    paths = glob.glob(os.path.join(dcm_root_dir, "**/*.dcm"), recursive=True)
    return paths

def randomizeID(id):
    string = str(id)
    splits = string.split('.')
    newID = splits[0]
    i = 0
    for split in splits:
        if i == 0:
            i += 1
            continue
        elif len(split) == 1:
            newID = '.'.join((newID, split))
            continue
        num = int(split) + random.randint(0, 9)
        newID = '.'.join((newID, str(num)))

    return newID

def anonSample(file, idtype, dict):
    id = file[idtype].value
    if id in dict.keys():
        anon_id = dict[id]
    else:
        if idtype == 'PatientID':
            anon_id = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(25))
        else:
            anon_id = randomizeID(id)
        # make sure that the new ID isn't the same as another
        while anon_id in dict.values():
            anon_id = randomizeID(id)
        dict[id] = anon_id

    return anon_id


def dcm_anonymize(dcm_files, output_path, stop=None):
    # creates dictionaries for the IDs for look up later
    samplePatientIDs = {}
    sampleStudyInstanceUIDs = {}
    sampleSeriesInstanceUID = {}
    sampleSOPInstanceUID = {}

    UIDs = {'PatientID' : samplePatientIDs,
            'StudyInstanceUID': sampleStudyInstanceUIDs,
            'SeriesInstanceUID': sampleSeriesInstanceUID,
            'SOPInstanceUID': sampleSOPInstanceUID}

    # UIDs = pickle.load(open(os.path.join(output_path, "UIDs.pkl"), "rb"))

    skipped = []

    # tags to anonymize
    anon_tags = ['InstanceCreationDate', 'InstanceCreationTime', 'AccessionNumber', 'StudyDate',
                 'SeriesDate', 'AcquisitionDate', 'ContentDate', 'StudyTime', 'SeriesTime', 'AcquisitionTime',
                 'ContentTime', 'AccessionNumber', 'InstitutionName', 'InstitutionAddress', 'ReferringPhysicianName',
                 'PhysiciansOfRecord', 'PerformingPhysicianName', 'OperatorsName', 'PatientName', 
                 'IssuerOfPatientID', 'PatientBirthDate', 'PatientSex', 'OtherPatientIDs', 'PatientAge', 'PatientSize',
                 'PatientWeight', 'PatientAddress', 'EthnicGroup', 'PregnancyStatus', 'RequestingPhysician',
                 'PerformedProcedureStepStartDate', 'PerformedProcedureStepStartTime', 'PerformedProcedureStepID']

    # for upto 200 dcm folders
    n = 0
    for file in dcm_files:
        try:  # if it doesn't
            dcm_file = pydicom.dcmread(file)
            dcm_file.remove_private_tags()
            out_path = output_path
            for UID in UIDs.keys():
                # get the UID and get the anonymized UID
                anon_id = anonSample(dcm_file, UID, UIDs[UID])
                dcm_file[UID].value = anon_id
                out_path = os.path.join(out_path, anon_id)

            out_path+=".dcm"
                # save instance UID to rename the filename (so that filename and SOPinstance matches)
            # for the other tags, make them anonymous
            for tag in anon_tags:
                if tag in dcm_file:
                    if type(dcm_file.data_element(tag).value) == str:
                        dcm_file.data_element(tag).value = 'N/A'
                    elif type(dcm_file.data_element(tag).value) == pydicom.uid.UID:
                        dcm_file.data_element(tag).value = 'N/A'
                    elif type(dcm_file.data_element(tag).value) == int:
                        dcm_file.data_element(tag).value = 0
                    else:
                        dcm_file.data_element(tag).value = 0.0
                
                pathlib.Path("/".join(out_path.split("/")[:-1])).mkdir(parents=True, exist_ok=True)
                dcm_file.save_as(out_path)
            n += 1
        except:
            print('Invalid Dicom Error, skipping')
            skip_file = pydicom.dcmread(file, force=True)
            skipped.append((skip_file.AccessionNumber, skip_file.StudyInstanceUID))
            continue
        if n == stop or n == len(dcm_files):
            pickle.dump(UIDs, open(os.path.join(output_path, "UIDs.pkl"), "wb"))
            exit()

        pickle.dump(UIDs, open(os.path.join(output_path, "UIDs.pkl"), "wb"))
        pickle.dump(skipped, open(os.path.join(output_path, "skipped.pkl"), "wb"))


if __name__ == "__main__":
    data_dir = sys.argv[1]
    output_dir = sys.argv[2]
    if len(sys.argv) > 3:
        # stopping number
        stop = int(sys.argv[3])
    else:
        stop = None
    print('Extracting DICOM folders', flush=True)
    dcm_folders = get_dcm_paths(data_dir)
    print('Starting DICOM Study Anonymization', flush=True)
    dcm_anonymize(dcm_folders, output_dir, stop=None)

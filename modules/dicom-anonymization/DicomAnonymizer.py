#!/usr/bin/env python
# coding: utf-8

"""To do list:
- some history of anonymization (to continue at later time)
- maybe some GUI (tkinter) to make it easier to use
"""

import os
import sys
import pydicom
import random
import glob
import pathlib
import pickle


def get_dcm_folders(dcm_root_dir):
    # get all folders
    print('getting all dcm folders')
    # speeding it up by checking files within each folder at the start
    dcm_flds = []
    for x in os.walk(dcm_root_dir):
        folder = x[0]
        # rejecting some folders that isn't in the accession list (HCC specific)
        if 'bk' in folder or 'March5' in folder:
            continue
        try:
            # assumes that all files in the study folder is dcm files
            if 'dcm' in os.listdir(folder)[0]:
                dcm_flds.append(folder)
        except:
            print('no dcm files in folder, skipping')
            continue
    return dcm_flds



# randomly anonymizes the input id
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


# uniquely anonymizes the ID and keeps in dictionary for lookup
def anonSample(file, idtype, dict):
    id = file[idtype].value
    if id in dict.keys():
        anon_id = dict[id]
    else:
        anon_id = randomizeID(id)
        # make sure that the new ID isn't the same as another
        while anon_id in dict.values():
            anon_id = randomizeID(id)
        dict[id] = anon_id

    return anon_id


def dcm_anonymize(dcm_folders, output_path, stop=None):
    # creates dictionaries for the IDs for look up later
    sampleStudyInstanceUIDs = {}
    sampleSeriesInstanceUID = {}
    sampleSOPInstanceUID = {}

    UIDs = {'StudyInstanceUID': sampleStudyInstanceUIDs,
            'SeriesInstanceUID': sampleSeriesInstanceUID,
            'SOPInstanceUID': sampleSOPInstanceUID}

    # UIDs = pickle.load(open(os.path.join(output_path, "UIDs.pkl"), "rb"))

    skipped = []

    # tags to anonymize
    anon_tags = ['InstanceCreationDate', 'InstanceCreationTime', 'AccessionNumber', 'StudyDate',
                 'SeriesDate', 'AcquisitionDate', 'ContentDate', 'StudyTime', 'SeriesTime', 'AcquisitionTime',
                 'ContentTime', 'AccessionNumber', 'InstitutionName', 'InstitutionAddress', 'ReferringPhysicianName',
                 'PhysiciansOfRecord', 'PerformingPhysicianName', 'OperatorsName', 'PatientName', 'PatientID',
                 'IssuerOfPatientID', 'PatientBirthDate', 'PatientSex', 'OtherPatientIDs', 'PatientAge', 'PatientSize',
                 'PatientWeight', 'PatientAddress', 'EthnicGroup', 'PregnancyStatus', 'RequestingPhysician',
                 'PerformedProcedureStepStartDate', 'PerformedProcedureStepStartTime', 'PerformedProcedureStepID']

    # for upto 200 dcm folders
    n = 0
    for dcm_folder in dcm_folders:
        files = [f for f in os.listdir(dcm_folder)]
        test_file_path = os.path.join(dcm_folder, files[random.randint(0, len(files) - 1)])
        print('testing folder: {}'.format(dcm_folder))
        # check if dcm folder has the invalid dicom error or not (no forced dicom file reading)
        try:  # if it doesn't
            test_file = pydicom.dcmread(test_file_path)
            anon_id = anonSample(test_file, 'StudyInstanceUID', UIDs['StudyInstanceUID'])
            # make folder with the anonymized studyUID name
            study_folder = os.path.join(output_path, anon_id)
            os.mkdir(study_folder)
            for file in files:
                dcm_file = pydicom.dcmread(os.path.join(dcm_folder, file))
                dcm_file.remove_private_tags()
                for UID in UIDs.keys():
                    # get the UID and get the anonymized UID
                    anon_id = anonSample(dcm_file, UID, UIDs[UID])
                    # save instance UID to rename the filename (so that filename and SOPinstance matches)
                    if UID == 'SOPInstanceUID':
                        new_filename = anon_id
                    dcm_file[UID].value = anon_id
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
                dcm_file.save_as(os.path.join(study_folder, new_filename + '.dcm'))
            n += 1
            print('total folders anonymized: {}/{}. Study: {}'.format(n, len(dcm_folders), study_folder), flush=True)
        except:
            print('Invalid Dicom Error, skipping')
            skip_file = pydicom.dcmread(test_file_path, force=True)
            skipped.append((skip_file.AccessionNumber, skip_file.StudyInstanceUID))
            continue
        if n == stop or n == len(dcm_folders):
            pickle.dump(UIDs, open(os.path.join(output_path, "UIDs.pkl"), "wb"))
            print('anonymized {} samples, exiting.'.format(stop), flush=True)
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
    dcm_folders = get_dcm_folders(data_dir)
    print('Starting DICOM Study Anonymization', flush=True)
    dcm_anonymize(dcm_folders, output_dir, stop=None)

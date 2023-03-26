#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import glob 
from shutil import copyfile
import hashlib
import json
import sys
import subprocess
import logging
from multiprocessing import Pool
import pdb
import time
import pickle
import argparse
import numpy as np
import pandas as pd
import pydicom as dicom 
# pydicom imports needed to handle data errors
from pydicom import config
from pydicom import datadict
from pydicom import values 
import dicom2nifti
import pathlib
configs = {}



def initialize_config_and_execute(config_values):
    global configs
    configs = config_values
    # Applying checks for paths
    
    p1 = pathlib.PurePath(configs['DICOMHome'])
    dicom_home = p1.as_posix() # the folder containing your dicom files

    p2 = pathlib.PurePath(configs['OutputDirectory'])
    output_directory = p2.as_posix()

    print_images = configs['PrintImages']
    print_only_common_headers = bool(configs['CommonHeadersOnly'])
    depth = int(configs['Depth'])
    processes = int(configs['UseProcesses']) # how many processes to use.
    flattened_to_level = configs['FlattenedToLevel']
    email = configs['YourEmail']
    send_email = configs['SendEmail']
    no_splits = int(configs['SplitIntoChunks'])
    is16Bit = bool(configs['is16Bit']) 
    
    metadata_col_freq_threshold = 0.1

    nifti_destination = output_directory + '/extracted-images/'
    failed = output_directory + '/failed-dicom/'
    maps_directory = output_directory + '/maps/'
    meta_directory = output_directory + '/meta/'

    LOG_FILENAME = output_directory + '/ImageExtractor.out'
    pickle_file = output_directory + '/ImageExtractor.pickle'
    dict_pickle_file = output_directory + '/ImageExtractork_dict.pickle'

    # record the start time
    t_start = time.time()

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

    if not os.path.exists(maps_directory):
        os.makedirs(maps_directory)

    if not os.path.exists(meta_directory):
        os.makedirs(meta_directory)

    if not os.path.exists(nifti_destination):
        os.makedirs(nifti_destination)

    if not os.path.exists(failed):
        os.makedirs(failed)

    if not os.path.exists(failed + "/1"):
        os.makedirs(failed + "/1")

    if not os.path.exists(failed + "/2"):
        os.makedirs(failed + "/2")

    if not os.path.exists(failed + "/3"):
        os.makedirs(failed + "/3")

    if not os.path.exists(failed + "/4"):
        os.makedirs(failed + "/4")

    logging.info("------- Values Initialization DONE -------")
    final_res = execute(pickle_file, dicom_home, output_directory, print_images, print_only_common_headers, depth,
                        processes, flattened_to_level, email, send_email, no_splits, is16Bit, nifti_destination,
        failed, maps_directory, meta_directory, LOG_FILENAME, metadata_col_freq_threshold, t_start,dict_pickle_file)
    return final_res


# Function for getting tuple for field,val pairs
def get_tuples(plan, outlist = None, key = ""):
    if len(key)>0:
        key =  key + "_"
    if not outlist:
        outlist = []
    for aa  in plan.dir():
        try:
            hasattr(plan,aa)
        except TypeError as e:
            logging.warning('Type Error encountered')
        if hasattr(plan, aa) and aa!= 'PixelData':
            value = getattr(plan, aa)
            start = len(outlist)
            # if dicom sequence extract tags from each element
            if type(value) is dicom.sequence.Sequence:
                for nn, ss in enumerate(list(value)):
                    newkey = "_".join([key,("%d"%nn),aa]) if len(key) else "_".join([("%d"%nn),aa])
                    candidate = get_tuples(ss,outlist=None,key=newkey)
                    # if extracted tuples are too big condense to a string
                    if len(candidate)>2000:
                        outlist.append((newkey,str(candidate)))
                    else:
                        outlist.extend(candidate)
            else:
                if type(value) is dicom.valuerep.DSfloat:
                    value = float(value)
                elif type(value) is dicom.valuerep.IS:
                    value = str(value)
                elif type(value) is dicom.valuerep.MultiValue:
                    value = tuple(value)
                elif type(value) is dicom.uid.UID:
                    value = str(value)
                outlist.append((key + aa, value))
                # appends name, value pair for this file. these are later concatenated to the dataframe
    return outlist


def extract_headers(f_list_elem):
    nn,ff = f_list_elem # unpack enumerated list
    ff = glob.glob(f'{ff}/*.dcm')[0]
    plan = dicom.dcmread(ff, force=True)  # reads in dicom file
    # checks if this file has an image
    c=True
    try:
        check = plan.pixel_array # throws error if dicom file has no image
    except:
        c = False
    kv = get_tuples(plan)       # gets tuple for field,val pairs for this file. function defined above
    # dicom images should not have more than 300
    if len(kv)>500:
        logging.debug(str(len(kv)) + " dicoms produced by " + ff)
    kv.append(('file', f_list_elem[1])) # adds my custom field with the original filepath
    kv.append(('has_pix_array',c))   # adds my custom field with if file has image
    if c:
        # adds my custom category field - useful if classifying images before processing
        kv.append(('category','uncategorized'))
    else:
        kv.append(('category','no image'))      # adds my custom category field, makes note as imageless
    return dict(kv)


# Function to extract pixel array information
# takes an integer used to index into the global filedata dataframe
# returns tuple of
# filemapping: dicom to nifti paths   (as str)
# fail_path: dicom to failed folder (as tuple)
# found_err: error code produced when processing
def extract_images(filedata, i, nifti_destination, flattened_to_level, failed, is16Bit):
    #ds = dicom.dcmread(filedata.iloc[i].loc['file'], force=True) # read file in
    #dicom2nifti.dicom_series_to_nifti(filedata.iloc[i].loc['file'], )
    found_err=None
    filemapping = ""
    fail_path = ""
    try:
        if flattened_to_level == 'patient':
            ID = filedata.iloc[i].loc['PatientID']  # Unique identifier for the Patient.
            folderName = hashlib.sha224(ID.encode('utf-8')).hexdigest()
            # check for existence of patient folder. Create if it does not exist.
            os.makedirs(nifti_destination + folderName,exist_ok=True)
        elif flattened_to_level == 'study':
            ID1 = filedata.iloc[i].loc['PatientID']  # Unique identifier for the Patient.
            try:
                ID2 = filedata.iloc[i].loc['StudyInstanceUID']  # Unique identifier for the Study.
            except:
                ID2='ALL-STUDIES'
            folderName = hashlib.sha224(ID1.encode('utf-8')).hexdigest() + "/" + \
                         hashlib.sha224(ID2.encode('utf-8')).hexdigest()
            # check for existence of the folder tree patient/study/series. Create if it does not exist.
            os.makedirs(nifti_destination + folderName,exist_ok=True)
            imName = hashlib.sha224(filedata.iloc[i].loc['SeriesDescription'].encode('utf-8')).hexdigest() 
        else:
            ID1=filedata.iloc[i].loc['PatientID']  # Unique identifier for the Patient.
            try:
                ID2=filedata.iloc[i].loc['StudyInstanceUID']  # Unique identifier for the Study.
                ID3=filedata.iloc[i].loc['SeriesInstanceUID']  # Unique identifier of the Series.
            except:
                ID2='ALL-STUDIES'
                ID3='ALL-SERIES'
            folderName = hashlib.sha224(ID1.encode('utf-8')).hexdigest() + "/" + \
                         hashlib.sha224(ID2.encode('utf-8')).hexdigest() + "/" + \
                         hashlib.sha224(ID3.encode('utf-8')).hexdigest()
            # check for existence of the folder tree patient/study/series. Create if it does not exist.
            os.makedirs(nifti_destination + folderName,exist_ok=True)


        niftifile = nifti_destination+folderName + '/' +ID1 +'_' +ID2 +'_' +ID3 + '.nii.gz'
        dicom2nifti.dicom_series_to_nifti(str(filedata.iloc[i].loc['file']),niftifile)
        filemapping = filedata.iloc[i].loc['file'] + ',' + niftifile + '\n'
    except AttributeError as error:
        found_err = error
        logging.error(found_err)
        fail_path = filedata.iloc[i].loc['file'], failed + '1/' + \
                    os.path.split(filedata.iloc[i].loc['file'])[1][:-4]+'.dcm'
    except ValueError as error:
        found_err = error
        logging.error(found_err)
        fail_path = filedata.iloc[i].loc['file'], failed + '2/' + \
                    os.path.split(filedata.iloc[i].loc['file'])[1][:-4]+'.dcm'
    except BaseException as error:
        found_err = error
        logging.error(found_err)
        fail_path = filedata.iloc[i].loc['file'], failed + '3/' + \
                    os.path.split(filedata.iloc[i].loc['file'])[1][:-4]+'.dcm'
    except Exception as error:
        found_err = error
        logging.error(found_err)
        fail_path = filedata.iloc[i].loc['file'], failed + '4/' + \
                    os.path.split(filedata.iloc[i].loc['file'])[1][:-4]+'.dcm'
    return (filemapping, fail_path, found_err)


# Function when pydicom fails to read a value attempt to read as other types.
def fix_mismatch_callback(raw_elem, **kwargs):
    try:
        if raw_elem.VR: 
            values.convert_value(raw_elem.VR, raw_elem)
    except BaseException as err:
        for vr in kwargs['with_VRs']:
            try:
                values.convert_value(vr, raw_elem)
            except ValueError:
                pass
            else:
                raw_elem = raw_elem._replace(VR=vr)
    return raw_elem


def get_path(depth, dicom_home):
    directory = dicom_home + '/'
    i = 0
    while i < depth:
        directory += "*/"
        i += 1
    return directory + "*.dcm"

    
# Function used by pydicom.
def fix_mismatch(with_VRs=['PN', 'DS', 'IS']):
    """A callback function to check that RawDataElements are translatable
    with their provided VRs.  If not, re-attempt translation using
    some other translators.
    Parameters
    ----------
    with_VRs : list, [['PN', 'DS', 'IS']]
        A list of VR strings to attempt if the raw data element value cannot
        be translated with the raw data element's VR.
    Returns
    -------
    No return value.  The callback function will return either
    the original RawDataElement instance, or one with a fixed VR.
    """
    dicom.config.data_element_callback = fix_mismatch_callback
    config.data_element_callback_kwargs = {
        'with_VRs': with_VRs,
    }    


def execute(pickle_file, dicom_home, output_directory, print_images, print_only_common_headers, depth,
            processes, flattened_to_level, email, send_email, no_splits, is16Bit, nifti_destination,
    failed, maps_directory, meta_directory, LOG_FILENAME, metadata_col_freq_threshold, t_start,dict_pickle_file):
    err = None
    fix_mismatch()
    if processes == 0.5:  # use half the cores to avoid  high ram usage
        core_count = int(os.cpu_count()/2)
    elif processes == 0:  # use all the cores
        core_count = int(os.cpu_count())
    elif processes < os.cpu_count():  # use the specified number of cores to avoid high ram usage
        core_count = processes
    else:
        core_count = int(os.cpu_count())
    # get set up to create dataframe
    dirs = os.listdir(dicom_home)
    # gets all dicom files. if editing this code, get filelist into the format of a list of strings,
    # with each string as the file path to a different dicom file.
    file_path = get_path(depth, dicom_home)

    if False : #os.path.isfile(pickle_file):
        with open(pickle_file,'rb') as f: 
            filelist=pickle.load(f)
        with open(dict_pickle_file,'rb') as f: 
            patient_dict = pickle.load(f)
    else:
        filelist=glob.glob(file_path, recursive=True) # search the folders at the depth we request and finds all dicoms
        pickle.dump(filelist,open(pickle_file,'wb'))
        #get all the patient folders
        patient_dict = {}
        volume_list  =[]
        volume_list  = glob.glob(f'{dicom_home}/**/*.dcm',recursive=True)
        volume_list = set([os.path.split(e)[0] for e in volume_list])
        volume_list = list(volume_list)
    file_chunks = np.array_split(volume_list,no_splits)
    logging.info('Number of dicom files: ' + str(len(filelist)))
    try:
        ff = filelist[0] # load first file as a template to look at all
    except IndexError:
        logging.error("There is no file present in the given folder in " + file_path)
        sys.exit(1)
    plan = dicom.dcmread(ff, force=True)
    logging.debug('Loaded the first file successfully')

    keys = [(aa) for aa in plan.dir() if (hasattr(plan, aa) and aa != 'PixelData')]
    # checks for images in fields and prints where they are
    for field in plan.dir():
        if (hasattr(plan, field) and field!='PixelData'):
            entry = getattr(plan, field)
            if type(entry) is bytes:
                logging.debug(field)
                logging.debug(str(entry))

    for i,chunk in enumerate(file_chunks):
        csv_destination = "{}/meta/metadata_{}.csv".format(output_directory,i)
        mappings = "{}/maps/mapping_{}.csv".format(output_directory,i)
        fm = open(mappings, "w+")
        filemapping = 'Original DICOM file location, NIFTI location \n'
        fm.write(filemapping)

        # add a check to see if the metadata has already been extracted
        # step through whole file list, read in file, append fields to future dataframe of all files

        headerlist = []
        # start up a multi processing pool
        # for every item in filelist send data to a subprocess and run extract_headers func
        # output is then added to headerlist as they are completed (no ordering is done)
        with Pool(core_count) as p:
            res= p.imap_unordered(extract_headers, enumerate(chunk))
            for i,e in enumerate(res):
                headerlist.append(e)
        data = pd.DataFrame(headerlist)
        logging.info('Chunk ' + str(i) + ' Number of fields per file : ' + str(len(data.columns)))
        # find common fields
        # make dataframe containing all fields and all files minus those removed in previous block
        # export csv file of final dataframe
        export_csv = data.to_csv(csv_destination, index = None, header=True)
        fields=data.keys()
        count = 0 # potential painpoint
        # writting of log handled by main process
        if print_images:
            logging.info("Start processing Images")
            pokemon = open('fail_log.txt','w')
            filedata = data
            total = len(chunk)
            stamp = time.time()
            for i in range(len(filedata)):
                (fmap,fail_path,err) = extract_images(filedata, i, nifti_destination, flattened_to_level, failed, is16Bit)
                if err:
                    count +=1
                    #copyfile(fail_path[0],fail_path[1])
                    print(f"err:{fail_path[1]}@{fail_path[0]}",file=pokemon)
                    err_msg = str(count) + ' out of ' + str(len(chunk)) + ' dicom images have failed extraction'
                    logging.error(err_msg)
                else:
                    fm.write(fmap)
            pokemon.close()
        fm.close()
        logging.info('Chunk run time: %s %s', time.time() - t_start, ' seconds!')

    logging.info('Generating final metadata file')

    col_names = dict()
    all_headers = dict()
    total_length = 0

    metas = glob.glob( "{}*.csv".format(meta_directory))
    # for each meta  file identify the columns that are not na's for at least 10% (metadata_col_freq_threshold) of data
    for meta in metas:
        m = pd.read_csv(meta,dtype='str')
        d_len = m.shape[0]
        total_length += d_len

        for e in m.columns:
            col_pop = d_len - np.sum(m[e].isna()) # number of populated rows for this column in this metadata file

            if e in col_names:
                col_names[e] += col_pop
            else:
                col_names[e] = col_pop
            
            # all_headers keeps track of number of appearances of each header. We later use this count to ensure that
            # the headers we use are present in all metadata files.
            if e in all_headers:
                all_headers[e] += 1
            else:
                all_headers[e] = 1

    loadable_names = list()
    for k in col_names.keys():
        if k in all_headers and all_headers[k] >= no_splits:  # no_splits == number of batches used 
            if col_names[k] >= metadata_col_freq_threshold*total_length:
                loadable_names.append(k) # use header only if it's present in every metadata file
            
    # load every metadata file using only valid columns
    meta_list = list()
    for meta in metas:
        m = pd.read_csv(meta,dtype='str',usecols=loadable_names)
        meta_list.append(m)
    merged_meta = pd.concat(meta_list,ignore_index=True)
    merged_meta.to_csv('{}/metadata.csv'.format(output_directory),index=False)
    # getting a single mapping file
    logging.info('Generatign final mapping file')
    mappings = glob.glob("{}/maps/*.csv".format(output_directory))
    map_list = list()
    for mapping in mappings:
        map_list.append(pd.read_csv(mapping,dtype='str'))
    merged_maps = pd.concat(map_list,ignore_index=True)
    if print_only_common_headers == True:
        mask_common_fields = merged_maps.isnull().mean() < 0.1
        common_fields = set(np.asarray(merged_maps.columns)[mask_common_fields])
        merged_maps = merged_maps[common_fields]
    merged_maps.to_csv('{}/mapping.csv'.format(output_directory),index=False)

    if send_email == True:
       subprocess.call('echo "Niffler has successfully completed the nifti conversion" | mail -s "The image conversion'
                       ' has been complete" {0}'.format(email), shell=True)
    # Record the total run-time
    logging.info('Total run time: %s %s', time.time() - t_start, ' seconds!')
    logging.shutdown()  # Closing logging file after extraction is done !!
    logs = []
    logs.append(err)
    logs.append("The nifti conversion is SUCCESSFUL")
    return logs


if __name__ == "__main__":
    with open('config.json', 'r') as f:
        niffler = json.load(f)

    # CLI Argument Parser
    ap = argparse.ArgumentParser()

    ap.add_argument("--DICOMHome", default=niffler['DICOMHome'])
    ap.add_argument("--OutputDirectory", default=niffler['OutputDirectory'])
    ap.add_argument("--Depth", default=niffler['Depth'])
    ap.add_argument("--SplitIntoChunks", default=niffler['SplitIntoChunks'])
    ap.add_argument("--PrintImages", default=niffler['PrintImages'])
    ap.add_argument("--CommonHeadersOnly", default=niffler['CommonHeadersOnly'])
    ap.add_argument("--UseProcesses", default=niffler['UseProcesses'])
    ap.add_argument("--FlattenedToLevel", default=niffler['FlattenedToLevel'])
    ap.add_argument("--is16Bit", default=niffler['is16Bit'])
    ap.add_argument("--SendEmail", default=niffler['SendEmail'])
    ap.add_argument("--YourEmail", default=niffler['YourEmail'])

    args = vars(ap.parse_args())

    if len(args) > 0:
        initialize_config_and_execute(args)
    else:
        initialize_config_and_execute(niffler)

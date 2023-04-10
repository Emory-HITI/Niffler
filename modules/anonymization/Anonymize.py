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
from multiprocessing.pool import ThreadPool as Pool
import pdb
import time
import pickle
import argparse
import numpy as np
import pandas as pd
import pydicom as dicom
import png
# pydicom imports needed to handle data errors. 
from pydicom import config
from pydicom import datadict
from pydicom import values
import preprocessor
import sys
# Add local directory to syspath for testing on both modules together without deploying.
# Add to the beginning of the list so it finds the dev version first.
sys.path.insert(0, '/home/zzaiman/working_zz/Anonymization/HITI_anon_internal')
from HITI_anon_internal.Anon import EmoryAnon
from HITI_anon_internal.DICOMAnonymization import DICOMAnon


np.seterr(invalid='ignore')

import pathlib
configs = {}

def initialize_config_and_execute(config_values):
    global configs
    configs = config_values
    # Applying checks for paths

    p1 = pathlib.PurePath(configs['DICOMHome'])
    dicom_home = p1.as_posix()  # the folder containing your dicom files

    p2 = pathlib.PurePath(configs['OutputDirectory'])
    output_directory = p2.as_posix()

    p3 = pathlib.PurePath(configs['MasterKeyPath'])
    mk_path = p3.as_posix()

    p4 = pathlib.PurePath(configs['DicomTagDictPath'])
    tag_dict_path = p4.as_posix()

    p5 = pathlib.PurePath(configs['KeepHeaderListPath'])
    keep_header_list_path = p5.as_posix()

    keep_header_list = []
    with open(keep_header_list_path, 'r') as f:
        lines = f.readlines()
        keep_header_list.extend(lines)

    p6 = pathlib.PurePath(configs['IgnoreDescPath'])
    ignore_desc_path = p6.as_posix()

    ignoreDesc = []
    with open(ignore_desc_path, 'r') as f:
        lines = f.readlines()
        ignoreDesc.extend(lines)

    print_png = bool(configs['PrintPng'])
    print_dicom = bool(configs['PrintDicom'])
    print_only_common_headers = bool(configs['CommonHeadersOnly'])
    PublicHeadersOnly = bool(configs['PublicHeadersOnly'])
    SpecificHeadersOnly = bool(configs['SpecificHeadersOnly'])
    depth = int(configs['Depth'])
    flattened_to_level = configs['FlattenedToLevel']
    email = configs['YourEmail']
    send_email = bool(configs['SendEmail'])
    batch_size = int(configs['BatchSize'])
    is16Bit = bool(configs['is16Bit'])
    mammo = bool(configs['Mammo'])

    metadata_col_freq_threshold = 0.1

    png_destination = output_directory + '/extracted-png/'
    dicom_anon_destination = output_directory + '/dicom-anon/'
    failed = output_directory + '/failed-dicom/'
    meta_directory = output_directory + '/meta/'
    metas = glob.glob("{}*.csv".format(meta_directory))

    LOG_FILENAME = output_directory + '/ImageExtractor.out'
    pickle_file = output_directory + '/ImageExtractor.pickle'

    # record the start time
    t_start = time.time()

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

    if not os.path.exists(meta_directory):
        os.makedirs(meta_directory)

    if not os.path.exists(png_destination):
        os.makedirs(png_destination)
    
    if not os.path.exists(dicom_anon_destination):
        os.makedirs(dicom_anon_destination)

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

    if not os.path.exists(failed + "/5"):
        os.makedirs(failed + "/5")

    # Load the Master Key
    Anon = EmoryAnon(mk_path, tag_dict_path)
    
    logging.info("------- Values Initialization DONE -------")
    final_res = execute(Anon, pickle_file, dicom_home, output_directory, print_png, print_dicom, print_only_common_headers, depth,
                        flattened_to_level, email, send_email, batch_size, is16Bit, png_destination,
                        failed, meta_directory, dicom_anon_destination, LOG_FILENAME, metadata_col_freq_threshold, t_start,
                        SpecificHeadersOnly, PublicHeadersOnly, ignoreDesc, keep_header_list, mammo)
    return final_res


# Function for getting tuple for field,val pairs
def get_tuples(plan, PublicHeadersOnly, outlist=None, key=""):
    if len(key) > 0:
        key = key + "_"
    if not outlist:
        outlist = []
    for aa in plan.dir():
        try:
            hasattr(plan, aa)
        except TypeError as e:
            logging.warning('Type Error encountered')
        if hasattr(plan, aa) and aa != 'PixelData':
            value = getattr(plan, aa)
            start = len(outlist)
            # if dicom sequence extract tags from each element
            if type(value) is dicom.sequence.Sequence:
                for nn, ss in enumerate(list(value)):
                    newkey = "_".join([key, ("%d" % nn), aa]) if len(key) else "_".join([("%d" % nn), aa])
                    candidate = get_tuples(ss, PublicHeadersOnly, outlist=None, key=newkey)
                    # if extracted tuples are too big condense to a string
                    if len(candidate) > 300:
                        outlist.append((newkey, str(candidate)))
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
    # appends the private tags
    if not PublicHeadersOnly:
        x = plan.keys()
        x = list(x)
        for i in x:
            if i.is_private:
                outlist.append((plan[i].name, plan[i].value))

    return outlist


def extract_headers(plan, filepath, PublicHeadersOnly, output_directory):
    # checks all dicom fields to make sure they are valid
    # if an error occurs, will delete it from the data structure
    dcm_dict_copy = list(plan._dict.keys())

    for tag in dcm_dict_copy:
        try:
            plan[tag]
        except:
            logging.warning("dropped fatal DICOM tag {}".format(tag))
            del plan[tag]

    c = True
    try:
        check = plan.pixel_array  # throws error if dicom file has no image
    except:
        c = False
    kv = get_tuples(plan, PublicHeadersOnly)  # gets tuple for field,val pairs for this file. function defined above

    if PublicHeadersOnly:
        dicom_tags_limit = 300
    else:
        dicom_tags_limit = 800

    if len(kv) > dicom_tags_limit:
        logging.debug(str(len(kv)) + " dicom tags produced by " + filepath)
        copyfile(filepath, output_directory + '/failed-dicom/5/' + os.path.basename(filepath))
    kv.append(('original_dicom_path', filepath))  # adds my custom field with the original filepath
    kv.append(('has_pix_array', c))  # adds my custom field with if file has image
    if c:
        # adds my custom category field - useful if classifying images before processing
        kv.append(('category', 'uncategorized'))
    else:
        kv.append(('category', 'no image'))  # adds my custom category field, makes note as imageless
    return dict(kv)


# Function to extract pixel array information
# takes an integer used to index into the global filedata dataframe
# returns tuple of
# filemapping: dicom to png paths   (as str)
# fail_path: dicom to failed folder (as tuple)
# found_err: error code produced when processing
def extract_images(ds, headers, png_destination, flattened_to_level, failed, is16Bit, mammo, anon_path):
    found_err = None
    filemapping = ""
    fail_path = ""

    try:
        im = ds.pixel_array  # pull image from read dicom
        anon_path_spl = anon_path[:-4].split('/')

        if flattened_to_level == 'patient':
            ID = anon_path_spl[-4]  # Unique identifier for the Patient.
            folderName = ID
            # check for existence of patient folder. Create if it does not exist.
            os.makedirs(png_destination + folderName, exist_ok=True)
        elif flattened_to_level == 'study':
            ID1 = anon_path_spl[-4]  # Unique identifier for the Patient.
            try:
                ID2 = anon_path_spl[-3]  # Unique identifier for the Study.
            except:
                ID2 = 'ALL-STUDIES'
            folderName = ID1 + "/" + \
                         ID2
            # check for existence of the folder tree patient/study/series. Create if it does not exist.
            os.makedirs(png_destination + folderName, exist_ok=True)
        else:
            ID1 = anon_path_spl[-4]  # Unique identifier for the Patient.
            try:
                ID2 = anon_path_spl[-3]  # Unique identifier for the Study.
                ID3 = anon_path_spl[-2]  # Unique identifier of the Series.
            except:
                ID2 = 'ALL-STUDIES'
                ID3 = 'ALL-SERIES'
            folderName = ID1 + "/" + \
                         ID2 + "/" + \
                         ID3
            # check for existence of the folder tree patient/study/series. Create if it does not exist.
            os.makedirs(png_destination + folderName, exist_ok=True)

        pngfile = png_destination + folderName + '/' + anon_path_spl[-1] + '.png'
        dicom_path = headers['original_dicom_path']
        image_path = png_destination + folderName + '/' + anon_path_spl[-1] + '.png'
        isRGB = headers['PhotometricInterpretation'] == 'RGB'


        if mammo: # specific preprocessing for Kheiron
            image = preprocessor.DigitalImage.fromFile(dicom_path)

                        # The following options are specifically requested by Kheiron to match what they have.
            options = preprocessor.ExportOptions()
            options.bitsPerSample = 16
            options.autoFlip = True
            options.skipPresentation = False

            image.exportToFilePNG(image_path, options)

        elif is16Bit:
            # write the PNG file as a 16-bit greyscale 
            image_2d = ds.pixel_array.astype(np.double)
            # # Rescaling grey scale between 0-255
            image_2d_scaled = (np.maximum(image_2d, 0) / image_2d.max()) * 65535.0
            # # Convert to uint
            shape = ds.pixel_array.shape
            image_2d_scaled = np.uint16(image_2d_scaled)
            with open(pngfile, 'wb') as png_file:
                if isRGB:
                    w = png.Writer(shape[1], shape[0], greyscale=False, bitdepth=16)
                else:
                    w = png.Writer(shape[1], shape[0], greyscale=True, bitdepth=16)
                w.write(png_file, image_2d_scaled)
        else:
            shape = ds.pixel_array.shape
            # Convert to float to avoid overflow or underflow losses.
            image_2d = ds.pixel_array.astype(float)
            # Rescaling grey scale between 0-255
            image_2d_scaled = (np.maximum(image_2d, 0) / image_2d.max()) * 255.0
            # onvert to uint
            image_2d_scaled = np.uint8(image_2d_scaled)
            # Write the PNG file
            with open(pngfile, 'wb') as png_file:
                if isRGB:
                    w = png.Writer(shape[1], shape[0], greyscale=False)
                else:
                    w = png.Writer(shape[1], shape[0], greyscale=True)
                w.write(png_file, image_2d_scaled)
        filemapping = headers['original_dicom_path'] + ', ' + pngfile + '\n'
    except AttributeError as error:
        found_err = error
        logging.error(found_err)
        fail_path = headers['original_dicom_path'], failed + '1/' + \
                    os.path.split(headers['original_dicom_path'])[1][:-4] + '.dcm'
    except ValueError as error:
        found_err = error
        logging.error(found_err)
        fail_path = headers['original_dicom_path'], failed + '2/' + \
                    os.path.split(headers['original_dicom_path'])[1][:-4] + '.dcm'
    except BaseException as error:
        found_err = error
        logging.error(found_err)
        fail_path = headers['original_dicom_path'], failed + '3/' + \
                    os.path.split(headers['original_dicom_path'])[1][:-4] + '.dcm'
    except Exception as error:
        found_err = error
        logging.error(found_err)
        fail_path = headers['original_dicom_path'], failed + '4/' + \
                    os.path.split(headers['original_dicom_path'])[1][:-4] + '.dcm'
    return (filemapping, fail_path, found_err)


# Function when pydicom fails to read a value attempt to read as other types.
def fix_mismatch_callback(raw_elem, **kwargs):
    try:
        if raw_elem.VR:
            values.convert_value(raw_elem.VR, raw_elem)
    except TypeError as err:
        logging.error(err)
    except BaseException as err:
        for vr in kwargs['with_VRs']:
            try:
                values.convert_value(vr, raw_elem)
            except ValueError:
                pass
            except TypeError:
                continue
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
def fix_mismatch(with_VRs=['PN', 'DS', 'IS', 'LO', 'OB']):
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

def execute(Anon, pickle_file, dicom_home, output_directory, print_png, print_dicom, print_only_common_headers, depth,
             flattened_to_level, email, send_email, batch_size, is16Bit, png_destination,
            failed, meta_directory, dicom_anon_destination, LOG_FILENAME, metadata_col_freq_threshold, t_start,
            SpecificHeadersOnly, PublicHeadersOnly, ignoreDesc, keep_header_list, mammo):
    err = None

    # Create dicom anonymization object.
    depth_mapping = {'patient' : 1, 'study' : 2, 'series' : 3}
    if flattened_to_level not in depth_mapping.keys():
        raise ValueError(f"Invalid flattened to level parameter {flattened_to_level}. Please use one of {depth_mapping.keys()}")


    dcma = DICOMAnon(Anon, depth_mapping[flattened_to_level]+1, dicom_anon_destination, ignoreDesc)


    fix_mismatch()
    # get set up to create dataframe
    dirs = os.listdir(dicom_home)
    # gets all dicom files. if editing this code, get filelist into the format of a list of strings,
    # with each string as the file path to a different dicom file.
    file_path = get_path(depth, dicom_home)

    if os.path.isfile(pickle_file):
        f = open(pickle_file, 'rb')
        filelist = pickle.load(f)
    else:
        filelist = glob.glob(file_path,
                             recursive=True)  # search the folders at the depth we request and finds all dicoms
        pickle.dump(filelist, open(pickle_file, 'wb'))
        
    # if the batch size is greater than the number of files, use one batch.
    if batch_size > len(filelist) and len(filelist) > 0:
        no_splits = 1
    else:
        no_splits = int(np.ceil(len(filelist) / batch_size))
        
    file_chunks = np.array_split(filelist, no_splits)
    logging.info('Number of dicom files: ' + str(len(filelist)))

    try:
        ff = filelist[0]  # load first file as a template to look at all
    except IndexError:
        logging.error("There is no file present in the given folder in " + file_path)
        sys.exit(1)

    plan = dicom.dcmread(ff, force=True)
    logging.debug('Loaded the first file successfully')

    keys = [(aa) for aa in plan.dir() if (hasattr(plan, aa) and aa != 'PixelData')]
    # checks for images in fields and prints where they are
    for field in plan.dir():
        if (hasattr(plan, field) and field != 'PixelData'):
            entry = getattr(plan, field)
            if type(entry) is bytes:
                logging.debug(field)
                logging.debug(str(entry))

    for i, chunk in enumerate(file_chunks):

        chunk_timestamp = time.time()

        csv_destination = "{}/meta/metadata_{}.csv".format(output_directory, i)
        # add a check to see if the metadata has already been extracted
        # step through whole file list, read in file, append fields to future dataframe of all files

        headerlist = []
        # Error counter.
        count = 0
        for filepath in chunk:
            plan = dicom.dcmread(filepath, force=True)
            headers = extract_headers(plan, filepath, PublicHeadersOnly, output_directory)
            
            # Always anonymize dicom in memory to anonymize keys in the MK but use the flag to determine whether to save.
            try:
                anon_path = dcma.run(plan, print_dicom)
                if anon_path is not None and print_dicom:
                    headers['anon_dicom_path'] = anon_path
            except Exception as e:
                logging.error(e)
                continue

            if print_png:
                if (headers['original_dicom_path'] is not np.nan):
                    (fmap, fail_path, err) = extract_images(plan, headers, png_destination, flattened_to_level, failed,
                                                            is16Bit, mammo, anon_path)
                    if err:
                        count += 1
                        copyfile(fail_path[0], fail_path[1])
                        err_msg = str(count) + ' out of ' + str(len(chunk)) + ' dicom images have failed extraction'
                        logging.error(err_msg)
                    else:
                        headers['png_path'] = fmap

            headerlist.append(headers)
        
        logging.info('Chunk run time: %s %s', time.time() - chunk_timestamp, ' seconds!')

        data = pd.DataFrame(headerlist)
        logging.info('Chunk ' + str(i) + ' Number of fields per file : ' + str(len(data.columns)))
        # export csv file of final dataframe
        if (SpecificHeadersOnly):
            try:
                feature_list = open("featureset.txt").read().splitlines()
                features = []
                for j in feature_list:
                    if j in data.columns:
                        features.append(j)
                meta_data = data[features]
            except:
                meta_data = data
                logging.error("featureset.txt not found")
        else:
            meta_data = data

        fields = data.keys()
        export_csv = meta_data.to_csv(csv_destination, index=None, header=True)
        count = 0  # potential painpoint
        # writting of log handled by main process
        

    logging.info('Generating final metadata file')

    col_names = dict()
    all_headers = dict()
    total_length = 0

    metas = glob.glob("{}*.csv".format(meta_directory))
    # for each meta  file identify the columns that are not na's for at least 10% (metadata_col_freq_threshold) of data
    if print_only_common_headers:
        for meta in metas:
            m = pd.read_csv(meta, dtype='str')
            d_len = m.shape[0]
            total_length += d_len

            for e in m.columns:
                col_pop = d_len - np.sum(m[e].isna())  # number of populated rows for this column in this metadata file

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
                if k not in keep_header_list and col_names[k] >= metadata_col_freq_threshold * total_length:
                    loadable_names.append(k)  # use header only if it's present in every metadata file

        # load every metadata file using only valid columns
        meta_list = list()
        for meta in metas:
            m = pd.read_csv(meta, dtype='str', usecols=loadable_names)
            meta_list.append(m)
        merged_meta = pd.concat(meta_list, ignore_index=True)
    
    else:
        # merging_meta
        merged_meta = pd.DataFrame()
        for meta in metas:
            m = pd.read_csv(meta, dtype='str')
            merged_meta = pd.concat([merged_meta, m], ignore_index=True)
        # for only common header
        if print_only_common_headers:
            mask_common_fields = merged_meta.isnull().mean() < 0.1
            common_fields = list(np.asarray(merged_meta.columns)[mask_common_fields])
            merged_meta = merged_meta[common_fields]

    merged_meta.to_csv('{}/metadata.csv'.format(output_directory), index=False)
    
    logging.info("Generated anonymized metadata file.")
    Anon.anon_tabular(f'{output_directory}/metadata.csv', f'{output_directory}')
    # Save anonymized keys.
    Anon.save_keys()


    if send_email:
        try:
            subprocess.call('echo "Niffler has successfully completed the png conversion" | mail -s "The image conversion'
                            ' has been complete" {0}'.format(email), shell=True)
        except Exception as e:
            logging.error(f"Unable to send email. {e}")
    # Record the total run-time
    logging.info('Total run time: %s %s', time.time() - t_start, ' seconds!')
    logging.shutdown()  # Closing logging file after extraction is done !!
    logs = []
    logs.append(err)
    logs.append("The PNG conversion is SUCCESSFUL")
    return logs


if __name__ == "__main__":
    with open('config.json', 'r') as f:
        niffler = json.load(f)

    # CLI Argument Parser
    ap = argparse.ArgumentParser()

    ap.add_argument("--DICOMHome", default=niffler['DICOMHome'])
    ap.add_argument("--OutputDirectory", default=niffler['OutputDirectory'])
    ap.add_argument("--MasterKeyPath", default=niffler['MasterKeyPath'])
    ap.add_argument("--DicomTagDictPath", default=niffler['DicomTagDictPath'])
    ap.add_argument("--Depth", default=niffler['Depth'])
    ap.add_argument("--BatchSize", default=niffler['BatchSize'])
    ap.add_argument("--PrintPng", default=niffler['PrintPng'])
    ap.add_argument("--PrintDicom", default=niffler['PrintDicom'])
    ap.add_argument("--Mammo", default=niffler['Mammo'])
    ap.add_argument("--IgnoreDescPath", default=niffler['IgnoreDescPath'])
    ap.add_argument("--CommonHeadersOnly", default=niffler['CommonHeadersOnly'])
    ap.add_argument("--PublicHeadersOnly", default=niffler['PublicHeadersOnly'])
    ap.add_argument("--SpecificHeadersOnly", default=niffler['SpecificHeadersOnly'])
    ap.add_argument("--FlattenedToLevel", default=niffler['FlattenedToLevel'])
    ap.add_argument("--is16Bit", default=niffler['is16Bit'])
    ap.add_argument("--SendEmail", default=niffler['SendEmail'])
    ap.add_argument("--KeepHeaderListPath", default=niffler['KeepHeaderListPath'])
    ap.add_argument("--YourEmail", default=niffler['YourEmail'])

    args = vars(ap.parse_args())

    if len(args) > 0:
        initialize_config_and_execute(args)
    else:
        initialize_config_and_execute(niffler)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

This script:
    1 - starts dcm4che to receive images from remote PACS.
    2 - reads txt files containing feature list to identify research profiles consisting of the interesting attributes.
    3 - grabs one instance per series and extract the metadata for the identified attributes and store in MongoDB.
    4 - deletes the dicom images periodically once the metadata is extracted.
    5 - keeps track of the volume of the dcm storage folder
"""

import os, os.path
import sys
import glob
import pymongo
import pydicom
import requests
import schedule
import time
import datetime
import threading
import logging
import pickle
import shutil
import subprocess
import pandas as pd
import json


with open('service/system.json', 'r') as f:
    niffler = json.load(f)

# Get constants from system.json
DCM4CHE_BIN = niffler['DCM4CHEBin']
STORAGE_FOLDER = niffler['StorageFolder']
FILE_PATH = niffler['FilePath']
QUERY_AET = niffler['QueryAet']

# Global Constants: Configurations and folder locations
EXTRACTION_RUNNING = False
IS_DCM4CHE_NOT_RUNNING = True
logging.basicConfig(level=logging.INFO)

FEATURES_FOLDER = "conf/"
PICKLE_FOLDER = "pickles/"


# Variables to track progress between iterations.
processed_series_but_yet_to_delete = list()
processed_and_deleted_series = list()            


# Get features of a txt file
features_lists = list()
feature_files = list()

# All processed series is saved between iterations as pickle files.
try:
    with open(PICKLE_FOLDER + 'processed_series_but_yet_to_delete.pickle', 'rb') as f:
        processed_series_but_yet_to_delete = pickle.load(f)
except:
    logging.info("Unable to load a valid pickle file. Initialized with empty value for processed_series_but_yet_to_delete")

try:
    with open(PICKLE_FOLDER + 'processed_and_deleted_series.pickle', 'rb') as f:
        processed_and_deleted_series = pickle.load(f)
except:
    logging.info("Unable to load a valid pickle file. Initialized with empty value for processed_and_deleted_series")



# Read the txt file which includes the features, then extract them
os.chdir(FEATURES_FOLDER)
txt_files = glob.glob('*.txt')
logging.info('Number of files consisting of the features to extract: %s', str(len(txt_files)))

for file in txt_files:
    filename, file_extension = os.path.splitext(file)
    text_file = open(file, "r")
    feature_list = text_file.read().split('\n')
    del feature_list[-1]
    features_lists.append(feature_list)
    feature_files.append(filename)



# Function for getting tuple for field, val pairs for this file
# plan is instance of dicom class, the data for single mammo file
def get_tuples(plan, features, outlist = None, key = ""):
    if len(key)>0:
        key =  key + "_"
    if not outlist:
        outlist = []
    for aa in features:
        if (aa!='PixelData'):
            try:
                value1 = plan[aa].value
                if type(value1) is pydicom.sequence.Sequence:
                    for nn, ss in enumerate(list(value1)):
                        newkey = "_".join([key,("%d"%nn),aa]) if len(key) else "_".join([("%d"%nn),aa])
                        outlist.extend(get_tuples(ss, outlist = None, key = newkey))
                else:
                    if type(value1) is pydicom.valuerep.DSfloat:
                        value1 = float(value1)
                    elif type(value1) is pydicom.valuerep.IS:
                        value1 = str(value1)
                    elif type(value1) is pydicom.valuerep.MultiValue:
                        value1 = tuple(value1)
                    elif type(value1) is pydicom.uid.UID:
                        value1 = str(value1)
                    outlist.append((key + aa, value1))  # appends name, value pair for this file. these are later concatenated to the dataframe
            except KeyError:
                logging.debug("Key error encountered for %s", aa)
    return outlist


# Get features of a dictionary
def get_dict_fields(bigdict, features):
    return {x: bigdict[x] for x in features if x in bigdict}



# The core method of extracting metadata
def extract():
    os.chdir(STORAGE_FOLDER)

    logging.info('Started the metadata extraction at: %s', str(datetime.datetime.now()))

    if len([name for name in os.listdir(".") if os.path.isdir(name)]) == 0:  # Print once if the storage folder is empty.
        logging.debug('There are no patients found. Waiting for new data to arrive.')

    while len([name for name in os.listdir(".") if os.path.isdir(name)]) == 0:  # Check whether the storage folder is still empty.
        time.sleep(10)  # sleep for 10 seconds before repeating the check.

    logging.debug('Number of patients: %s', len([name for name in os.listdir(STORAGE_FOLDER)]))

    try:
        extract_metadata()
    except TypeError:
        logging.debug('There are no objects found. Waiting for new data to arrive.')



# Extract a list of one instance from each series
def extract_metadata():
    global processed_series_but_yet_to_delete
    global processed_and_deleted_series
    global EXTRACTION_RUNNING
    global features_lists
    global feature_files

    extracted_in_this_iteration = 0
    first_inst_of_series = list()
    headerlist = []
    

    if EXTRACTION_RUNNING:
        logging.info("Previous Extraction Thread Still Running. Skip this iteration.......................")
    else:
        t_start = time.time()
        EXTRACTION_RUNNING = True
    
        series_string = subprocess.check_output("find -maxdepth 3 -mindepth 3 -type d", shell=True)
        series = series_string.splitlines()
        logging.info('Number of series: %s', len(series))


        # remove the series that were processed before
        for temp_id in series:
            if temp_id.decode("utf-8") in processed_series_but_yet_to_delete or temp_id.decode("utf-8") in processed_and_deleted_series:
                series.remove(temp_id)

        logging.info('Number of series to be processed: %s', len(series))
    

        for series_path in series:
            extracted_in_this_iteration += 1
            logging.debug('Extracted: %s %s %s %s', str(extracted_in_this_iteration), ' out of ', str(len(series)),
                          ' series.')

            if extracted_in_this_iteration % 100 == 0:
                logging.info('Extracted: %s %s %s %s', str(extracted_in_this_iteration), ' out of ', str(len(series)),
                              ' series.')

            # get and store series-level information
            try:
                first_instance = series_path.decode("utf-8") + "/" + os.listdir(series_path.decode("utf-8"))[0]
                ds = pydicom.dcmread(first_instance, force=True)

                for index, features in enumerate(features_lists):
                    kv = get_tuples(ds, features)  # gets tuple for field,val pairs for this file. function defined above
                    doc = get_dict_fields(dict(kv), features)
                    # insert to a Mongo DB collection
                    doc = {k: 'NaN' if not v else v for k, v in doc.items()}
                    if series_path not in processed_series_but_yet_to_delete and series_path not in processed_and_deleted_series:
                        processed_series_but_yet_to_delete.append(series_path.decode("utf-8"))                        
                        DB[str(feature_files[index])].insert_one(doc)
                        logging.debug('Added the series to the processed list: %s', series_path)

            except ConnectionResetError:
                logging.warn('The connection was reset during the extraction')
            except IsADirectoryError:
                logging.debug('The Series full path has an invalid character \\ that prevents extracting metadata')
            except FileNotFoundError:
                logging.debug('The file %s is not found', series_path.decode("utf-8"))
            except IndexError:
                logging.debug('Index error while attempting to access the Series %s', series_path.decode("utf-8"))
            except:
                logging.warn('The script could not extract the series %s', series_path.decode("utf-8"))
        logging.info('Metadata Extraction Completed at: %s', str(datetime.datetime.now()))

        # Record the total run-time
        logging.info('Total run time: %s %s', (time.time() - t_start)/60, ' minutes!')
        EXTRACTION_RUNNING = False


# Delete the processed DICOM objects from the storage.
def clear_storage():
    os.chdir(STORAGE_FOLDER)

    global processed_series_but_yet_to_delete
    global processed_and_deleted_series

    deleted_in_this_iteration = 0

    logging.info('Clean up process initiated at series level at: %s', str(datetime.datetime.now()))

    for del_series in processed_series_but_yet_to_delete:
        try:
            shutil.rmtree(STORAGE_FOLDER + del_series)
            processed_and_deleted_series.append(del_series)
            processed_series_but_yet_to_delete.remove(del_series)

            logging.debug('Deleting: %s', del_series)     

            deleted_in_this_iteration += 1
            logging.debug('Deleted: %s %s %s %s', str(deleted_in_this_iteration), ' out of ',
                         str(len(processed_series_but_yet_to_delete)), ' remaining extraction completed series.')
            if deleted_in_this_iteration % 1000 == 0:
                logging.info('Deleted: %s %s %s %s', str(deleted_in_this_iteration), ' out of ',
                          str(len(processed_series_but_yet_to_delete)), ' remaining extraction completed series.')
    
        except FileNotFoundError:
            logging.debug('The series of id %s was not found. Hence, not deleted in this iteration. Probably it was already deleted in a previous iteration without being tracked or by an external process', del_series)
        except ConnectionResetError:
            logging.debug('The connection was reset during the deletion')
        except OSError:
            logging.debug('New images arriving for the series. Therefore, do not delete the series: %s', del_series)

    logging.info('Clean up process completed at: %s %s %s %s', str(datetime.datetime.now()), ' for ',
                 deleted_in_this_iteration, ' series.')
    update_pickle()
    

# Write the pickle file periodically to track the progress and persist it to the filesystem
def update_pickle():
    global processed_series_but_yet_to_delete
    global processed_and_deleted_series

    # Pickle using the highest protocol available.
    with open(PICKLE_FOLDER + 'processed_series_but_yet_to_delete.pickle', 'wb') as f:
        pickle.dump(processed_series_but_yet_to_delete, f, pickle.HIGHEST_PROTOCOL)
    with open(PICKLE_FOLDER + 'processed_and_deleted_series.pickle', 'wb') as f:
        pickle.dump(processed_and_deleted_series, f, pickle.HIGHEST_PROTOCOL)

    logging.debug('dumping complete')


# Measure storage folder disk space utilization
def measure_diskutil():
    total, used, free = shutil.disk_usage(STORAGE_FOLDER)
    logging.info("Disk space used by the Storage Folder: %d GB" % (used // (2**30)))


# Run DCM4CHE only once, when the extraction script starts, and keep it running in a separate thread.
def run_dcm4che():
    global IS_DCM4CHE_NOT_RUNNING
    if IS_DCM4CHE_NOT_RUNNING:
        IS_DCM4CHE_NOT_RUNNING = False   
        logging.info('Starting DCM4CHE..')
        os.chdir(DCM4CHE_BIN)
        subprocess.call("{0}/storescp --accept-unknown --directory {1} --filepath {2} -b {3} > nohup.out &".format(DCM4CHE_BIN, STORAGE_FOLDER, FILE_PATH, QUERY_AET), shell=True)

        logging.info('Started DCM4CHE successfully..')

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


logging.info('The execution started at: %s', str(datetime.datetime.now()))

logging.debug('Debug logs enabled.')

# Create connections for communicating with Mongo DB server, to store metadata
try:
    if os.environ['MONGO_URI'] != "":
        mongo_uri = 'mongodb://' + os.environ['MONGO_URI']
    else:
        mongo_uri = 'mongodb://' + sys.argv[1]
except KeyError:
    mongo_uri = 'mongodb://' + sys.argv[1]

client = pymongo.MongoClient(mongo_uri)
DB = client.ScannersInfo


# The thread scheduling
schedule.every(5).minutes.do(run_threaded, run_dcm4che)
schedule.every(1).hours.do(run_threaded, measure_diskutil)
schedule.every(1).day.at("23:59").do(run_threaded, clear_storage)
schedule.every(20).minutes.do(run_threaded, update_pickle)
schedule.every(10).minutes.do(run_threaded, extract)

# Keep running in a loop.
while True:
    schedule.run_pending()
    time.sleep(1)

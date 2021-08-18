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
from re import findall
import sys
import glob
from warnings import resetwarnings
from bson.objectid import ObjectId
import pymongo
from pymongo.message import delete, query
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
import time
import pdb
from datetime import datetime, timedelta
from pymongo import MongoClient
from collections import Counter

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

# Data Loading Function
def load_json_data(url, user, passcode, db_json=None, first_index=None, second_index=None):

    # Parameters:
    # 1. url          - URL to get the data.
    # 2. user         - Username for Authorization of ResearchPACS Server.
    # 3. passcode     - Passcode for Authorization of ResearchPACS Server.
    # 4. db_json      - Name of the MongoDB Collection.
    # 5. first_index  - First index in the MongoDB Collection. (Usually a date time attribute)
    # 6. second_index - Second index in the MongoDB Collection. (Usually empi information attribute)

    load_time = time.time()
    data_collection = db[db_json]
    data = requests.get(url, auth=(user, passcode))
    data = data.json()

    data_collection.insert_one(data)
    data_collection.create_index(
        [
            (first_index, 1),
            (second_index, 1)
        ]
    )

    for i in data['links']:
        if (i['rel'] == 'next'):
            url = i['href']
            load_json_data(url, user, passcode, db_json, first_index, second_index)

    time_taken = round(time.time()-load_time, 2)
    logging.info('Spent {} seconds loading data into {}.'.format(time_taken, db_json))

# Data Clearing Function
def clear_data(db_json=None):

    # Parameters
    # 1. db_json - Name of the MongoDB Collection.

    clear_time = time.time()
    data_collection = db[db_json]
    cursor = data_collection.find({})

    for i in range(len(list(cursor))):
        items_collection = cursor[i]['items']
        previous_time = datetime.now()-timedelta(days=1)
        previous_date = previous_time.date()

        remove_list = []
        for i in range(len(items_collection)):
            item_date = datetime.strptime(items_collection[i]['lab_date'], '%Y-%m-%dT%H:%M:%SZ').date()
            diff_time = previous_date-item_date
            if (diff_time.total_seconds()>=0):
                remove_list.append(items_collection[i])

        for x in remove_list:
            if x in items_collection:
                items_collection.remove(x)

        item_id = data_collection.find_one()['_id']
        db[db_json].update_one({'_id':ObjectId(item_id)}, {'$set':{'items':items_collection}})

    time_taken = round(time.time()-clear_time, 2)
    logging.info('Spent {} seconds clealearing the data from {}.'.format(time_taken, db_json))
    
# Data Filtering Function
def view_data(db_json=None, user_query=None):
    view_time = time.time()
    data_collection = db[db_json]
    data_cursor = data_collection.find({})
    for document in data_cursor:
        data = document

    list_dict = []
    if (user_query):
        required_columns = user_query
    else:
        required_columns = data['items'].keys()

    for i in range(len(data['items'])):
        list_dict.append(data['items'][i])

    df = pd.DataFrame(list_dict)
    df = df[required_columns]

    time_taken = round(time.time()-view_time, 2)
    logging.info('Spent {} seconds viewing the data of {}.'.format(time_taken, db_json))
    return (df.head())


if __name__ == "__main__":
    log_format = '%(levelname)s %(asctime)s - %(message)s'
    logging.basicConfig(filename='rta_extraction.logs', level=logging.INFO,
                        format=log_format, filemode='w')
    logging = logging.getLogger()

    with open('service/system.json', 'r') as f:
        niffler = json.load(f)

    # Get constants from system.json
    Labs_FolderPath = niffler['LabsFilePath']
    Meds_FolderPath = niffler['MedsFilePath']
    Orders_FolderPath = niffler['OrdersFilePath']
    Labs_ExtractionFrequency = niffler['LabsDataExtractionFrequency']
    Meds_ExtractionFrequency = niffler['MedsDataExtractionFrequency']
    Orders_ExtractionFrequency = niffler['OrdersDataExtractionFrequency']
    Mongo_URI = niffler['MongoURI']
    UserName = niffler['UserName']
    PassCode = niffler['PassCode']

    # Connect to MongoDB
    connection_start_time = time.time()
    try:
        client = MongoClient(Mongo_URI)
        logging.info('MongoDB Connection Successful.')
    except:
        logging.error('MongoDB Connection Unsuccessful.')
    logging.info('Time taken to establish MongoDB Connection - {}'.format(round(time.time() - connection_start_time), 2))

    db = client.database
    
    schedule.every(Labs_ExtractionFrequency).minutes.do(run_threaded, 
                                                        load_json_data(url='https://prd-rta-app01.eushc.org:8443/ords/radiology/RTA/labs/', 
                                                        user=UserName, passcode=PassCode, db_json='labs_json', 
                                                        first_index='lab_date', second_index='empi'))
    schedule.every(Labs_ExtractionFrequency).minutes.do(run_threaded, 
                                                        load_json_data(url='https://prd-rta-app01.eushc.org:8443/ords/radiology/RTA/meds/', 
                                                        user=UserName, passcode=PassCode, db_json='meds_json', 
                                                        first_index='update_dt_tm', second_index='empi'))
    schedule.every(Labs_ExtractionFrequency).minutes.do(run_threaded, 
                                                        load_json_data(url='https://prd-rta-app01.eushc.org:8443/ords/radiology/RTA/orders/',
                                                        user=UserName, passcode=PassCode, db_json='orders_json', 
                                                        irst_index='completed_dt_tm', second_index='empi'))

    schedule.every(1).day.at("23:59").do(run_threaded, clear_data(db_json='labs_json'))
    schedule.every(1).day.at("23:59").do(run_threaded, clear_data(db_json='meds_json'))
    schedule.every(1).day.at("23:59").do(run_threaded, clear_data(db_json='orders_json'))

    while True:
        schedule.run_pending()
        time.sleep(1)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script:
    1 - starts dcm4che to receive images from remote PACS.
    2 - reads txt files containing feature list to identify research profiles consisting of the interesting attributes.
    3 - grabs one instance per series and extract the metadata for the identified attributes and store in MongoDB.
    4 - deletes the dicom images periodically once the metadata is extracted.
    5 - keeps track of the volume of the dcm storage folder.
"""

import os, os.path
from re import findall
import sys
import glob
from warnings import resetwarnings
from bson.objectid import ObjectId
import pymongo
from pymongo import database
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

# Data Loading Function
def load_data(url, user, passcode, db_json=None, first_index=None, second_index=None):
    '''
    Loads the json data from labs, meds and orders into corresponsing MongoDB Collection.
    '''
    # Parameters:
    # 1. url          - URL to get the data.
    # 2. user         - Username for Authorization of ResearchPACS Server.
    # 3. passcode     - Passcode for Authorization of ResearchPACS Server.
    # 4. db_json      - Name of the MongoDB Collection.
    # 5. first_index  - First index in the MongoDB Collection. (Usually a date time attribute)
    # 6. second_index - Second index in the MongoDB Collection. (Usually empi information attribute)

    global total_data
    load_time = time.time()
    data_collection = db[db_json]
    data = requests.get(url, auth=(user, passcode))
    data = data.json()
    items_data = data['items']

    for record in items_data:
        if record not in total_data:
            data_collection.insert_one(record)
            total_data.append(record)
            data_collection.create_index(
                [
                    (first_index, 1),
                    (second_index, 1)
                ]
            )
    logging.info(len(total_data))
    view_data(db_json)

    for i in data['links']:
        if (i['rel'] == 'next'):
            url = i['href']
            load_data(url, user, passcode, db_json, first_index, second_index)

    time_taken = round(time.time()-load_time, 2)
    logging.info('Spent {} seconds loading data into {}.'.format(time_taken, db_json))

# Data Clearing Function
def clear_data(db_json=None):
    '''
    Clears the data which is older than one day from MongoDB Collection.
    '''
    # Parameters:
    # 1. db_json - Name of the MongoDB Collection.

    clear_time = time.time()
    data_collection = db[db_json]
    cursor = data_collection.find({})

    if db_json == 'labs_json':
        date_column = 'lab_date'
    elif db_json == 'meds_json':
        date_column = 'update_dt_tm'
    elif db_json == 'orders_json':
        date_column = 'completed_dt_tm'

    for document in cursor:
        previous_time = datetime.now()-timedelta(days=1)
        previous_date = previous_time.date()

        item_date = datetime.strptime(document[date_column], '%Y-%m-%dT%H:%M:%SZ').date()
        diff_time = previous_date-item_date

        if (diff_time.total_seconds()>=0):
            data_collection.delete_one(document)

    time_taken = round(time.time()-clear_time, 2)
    logging.info('Spent {} seconds clearing the data from {}.'.format(time_taken, db_json))

# Data Viewing and Filtering Function
def view_data(db_json=None, user_query=None):
    '''
    Display the shape, outliers and value counts of the dataframe.
    '''
    # Parameters:
    # 1. db_json    - Name of the MongoDB Collection.
    # 2. user_query - List of features.

    view_time = time.time()
    data_collection = db[db_json]
    data_cursor = data_collection.find({})

    doc_list = []
    for document in data_cursor:
        doc_list.append(document)

    if db_json == 'labs_json':
        date_column = 'lab_date'
        labs_df = pd.DataFrame(doc_list)
        labs_df[date_column] = pd.to_datetime(labs_df[date_column].str.split('T').str[0])
        logging.info(labs_df.shape)
        logging.info(str(labs_df[date_column].value_counts().to_dict()))

        logging.info('Outliers - {}'.format(labs_df[date_column][datetime.now()-labs_df[date_column] > timedelta(30)].shape[0]))
        logging.info('Outliers Percentage - {}'.format(labs_df[date_column][datetime.now()-labs_df[date_column] > timedelta(30)].shape[0]/labs_df[date_column].shape[0]))

    elif db_json == 'meds_json':
        date_column = 'update_dt_tm'
        meds_df = pd.DataFrame(doc_list)
        meds_df[date_column] = pd.to_datetime(meds_df[date_column].str.split('T').str[0])
        logging.info(meds_df.shape)
        logging.info(str(meds_df[date_column].value_counts().to_dict()))

        logging.info('Outliers - {}'.format(meds_df[date_column][datetime.now()-meds_df[date_column] > timedelta(30)].shape[0]))
        logging.info('Outliers Percentage - {}'.format(meds_df[date_column][datetime.now()-meds_df[date_column] > timedelta(30)].shape[0]/meds_df[date_column].shape[0]))

    elif db_json == 'orders_json':
        date_column = 'completed_dt_tm'
        orders_df = pd.DataFrame(doc_list)
        orders_df[date_column] = pd.to_datetime(orders_df[date_column].str.split('T').str[0])
        logging.info(orders_df.shape)
        logging.info(str(orders_df[date_column].value_counts().to_dict()))

        logging.info('Outliers - {}'.format(orders_df[date_column][datetime.now()-orders_df[date_column] > timedelta(30)].shape[0]))
        logging.info('Outliers Percentage - {}'.format(orders_df[date_column][datetime.now()-orders_df[date_column] > timedelta(30)].shape[0]/orders_df[date_column].shape[0]))
        
    time_taken = round(time.time()-view_time, 2)
    logging.info('Spent {} seconds viewing the data of {}.'.format(time_taken, db_json))

def load_labs_data():
    '''
    A buffer function between main and load_data functions for labs data.
    '''
    global total_data
    global UserName
    global PassCode

    now = datetime.now()
    logging.info('Loading Labs Data')
    logging.info(now.strftime('%Y-%m-%d %H:%M:%S'))

    load_data(url=LabsURL, user=UserName, passcode=PassCode, db_json='labs_json', first_index='lab_date', second_index='empi')

def load_meds_data():
    '''
    A buffer function between main and load_data functions for meds data.
    '''
    global total_data
    global UserName
    global PassCode

    now = datetime.now()
    logging.info('Loading Meds Data')
    logging.info(now.strftime('%Y-%m-%d %H:%M:%S'))

    load_data(url=MedsURL, user=UserName, passcode=PassCode, db_json='meds_json', first_index='update_dt_tm', second_index='empi')

def load_orders_data():
    '''
    A buffer function between main and load_data functions for orders data.
    '''
    global total_data
    global UserName
    global PassCode

    now = datetime.now()
    logging.info('Loading Orders Data')
    logging.info(now.strftime('%Y-%m-%d %H:%M:%S'))
    
    load_data(url=OrdersURL, user=UserName, passcode=PassCode, db_json='orders_json', first_index='completed_dt_tm', second_index='empi')

def clear_labs_data():
    '''
    A buffer function between main and clear_data functions for labs data.
    '''
    now = datetime.now()
    logging.info('Clearing Labs Data')
    logging.info(now.strftime('%Y-%m-%d %H:%M:%S'))
    clear_data(db_json='labs_json')

def clear_meds_data():
    '''
    A buffer function between main and clear_data functions for meds data.
    '''
    now = datetime.now()
    logging.info('Clearing Meds Data')
    logging.info(now.strftime('%Y-%m-%d %H:%M:%S'))
    clear_data(db_json='meds_json')

def clear_orders_data():
    '''
    A buffer function between main and clear_data functions for orders data.
    '''
    now = datetime.now()
    logging.info('Clearing Orders Data')
    logging.info(now.strftime('%Y-%m-%d %H:%M:%S'))
    clear_data(db_json='orders_json')

def print_function():
    now = datetime.now()
    print ('Time - {}'.format(now))
    print ('Hit the print function')

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

if __name__ == "__main__":
    log_format = '%(levelname)s %(asctime)s - %(message)s'
    logging.basicConfig(filename='rta_extraction.logs', level=logging.INFO,
                        format=log_format, filemode='w')
    logging = logging.getLogger()

    with open('system.json', 'r') as f:
        niffler = json.load(f)

    # Get constants from system.json
    LabsURL = niffler['LabsURL']
    MedsURL = niffler['MedsURL']
    OrdersURL = niffler['OrdersURL']
    Labs_ExtractionFrequency = niffler['LabsDataExtractionFrequency']
    Meds_ExtractionFrequency = niffler['MedsDataExtractionFrequency']
    Orders_ExtractionFrequency = niffler['OrdersDataExtractionFrequency']
    UserName = niffler['UserName']
    PassCode = niffler['PassCode']
    Mongo_URI = niffler['MongoURI']
    Mongo_UserName = niffler['MongoUserName']
    Mongo_PassCode = niffler['MongoPassCode']

    # Connect to MongoDB
    connection_start_time = time.time()
    try:
        client = MongoClient(Mongo_URI, username=Mongo_UserName, password=Mongo_PassCode)
        logging.info('MongoDB Connection Successful.')
    except:
        logging.error('MongoDB Connection Unsuccessful.')
    logging.info('Time taken to establish MongoDB Connection - {}'.format(round(time.time() - connection_start_time), 2))

    db = client.database
    total_data = []

    schedule.every(Meds_ExtractionFrequency).minutes.do(run_threaded, load_labs_data)
    schedule.every(Meds_ExtractionFrequency).minutes.do(run_threaded, load_meds_data)
    schedule.every(Meds_ExtractionFrequency).minutes.do(run_threaded, load_orders_data)

    schedule.every(1).day.at("03:00").do(run_threaded, clear_labs_data)
    schedule.every(1).day.at("03:15").do(run_threaded, clear_meds_data)
    schedule.every(1).day.at("03:25").do(run_threaded, clear_orders_data)

    while True:
        schedule.run_pending()
        time.sleep(1)

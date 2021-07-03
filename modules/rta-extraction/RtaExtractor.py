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
from datetime import datetime, timedelta
from pymongo import MongoClient

logging.basicConfig(filename='rta_extraction.logs', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')

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

# Connect to MongoDB
connection_start_time = time.time()
try:
    client = MongoClient(Mongo_URI)
    logging.info('MongoDB Connection Successful.')
except:
    logging.error('MongoDB Connection Unsuccessful.')
logging.info('Time taken to establish MongoDB Connection - {}'.format(round(time.time() - connection_start_time), 2))

db = client.database

# Data Dumping Functions
def dump_labs_json_data():
    labs_dump_time = time.time()
    labs_collection = db.labs_json
    for file in os.listdir(Labs_FolderPath):
        if file.endswith('.json'):
            Labs_FilePath = Labs_FolderPath+file

    f = open(Labs_FilePath, 'r')
    labs_data = json.load(f)
    f.close()
    labs_collection.insert_one(labs_data)
    labs_collection.create_index('lab_date')
    logging.info('Labs data is dumped into MongoDB. The collection name is - labs_json')
    logging.info('Time taken to dump labs data in MongoDB - {}'.format(round(time.time() - labs_dump_time), 2))

def dump_meds_json_data():
    meds_dump_time = time.time()
    meds_collection = db.meds_json
    for file in os.listdir(Meds_FolderPath):
        if file.endswith('.json'):
            Meds_FilePath = Meds_FolderPath+file

    f = open(Meds_FilePath, 'r')
    meds_data = json.load(f)
    meds_collection.insert_one(meds_data)
    f.close()
    logging.info('Meds data is dumped into MongoDB. The collection name is - meds_json')
    logging.info('Time taken to dump meds data in MongoDB - {}'.format(round(time.time() - meds_dump_time), 2))

def dump_orders_json_data():
    orders_dump_time = time.time()
    orders_collection = db.orders_json
    for file in os.listdir(Orders_FolderPath):
        if file.endswith('.json'):
            Orders_FilePath = Orders_FolderPath+file

    f = open(Orders_FilePath, 'r')
    orders_data = json.load(f)
    orders_collection.insert_one(orders_data)
    f.close()
    logging.info('Orders data is dumped into MongoDB. The collection name is - orders_json')
    logging.info('Time taken to dump orders data in MongoDB - {}'.format(round(time.time() - orders_dump_time), 2))

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

# Clean Storage Functions
def clean_labs_collection():
    labs_clear_time = time.time()
    labs_collection = db.labs_json
    items_collection =  labs_collection.find_one()['items']

    cut_off_time = datetime.now() - timedelta(days=1)
    cut_off_date = cut_off_time.date()
    for item in items_collection:
        lab_datetime = datetime.strptime(item['lab_date'][:-1], '%Y-%m-%dT%H:%M:%S')
        lab_datetime = lab_datetime.date()
        if (lab_datetime < cut_off_date):
            items_collection.remove(item)

    item_id = labs_collection.find_one()['_id']
    db.labs_json.update_one({'_id':ObjectId(item_id)}, {'$set':{'items':items_collection}})
    logging.info('Time taken to clear labs data in MongoDB - {}'.format(time.time() - labs_clear_time))

def clean_meds_collection():
    meds_clear_time = time.time()
    meds_collection = db.meds_json
    items_collection =  meds_collection.find_one()['items']

    cut_off_time = datetime.now() - timedelta(days=1)
    cut_off_date = cut_off_time.date()
    for item in items_collection:
        meds_datetime = datetime.strptime(item['update_dt_tm'][:-1], '%Y-%m-%dT%H:%M:%S')
        meds_datetime = meds_datetime.date()
        if (meds_datetime < cut_off_date):
            items_collection.remove(item)

    item_id = meds_collection.find_one()['_id']
    db.meds_json.update_one({'_id':ObjectId(item_id)}, {'$set':{'items':items_collection}})
    logging.info('Time taken to clear meds data in MongoDB - {}'.format(time.time() - meds_clear_time))

def clean_orders_collection():
    orders_clean_time = time.time()
    orders_collection = db.orders_json
    items_collection =  orders_collection.find_one()['items']

    cut_off_time = datetime.now() - timedelta(days=1)
    cut_off_date = cut_off_time.date()
    for item in items_collection:
        orders_datetime = datetime.strptime(item['requested_dt_tm'][:-1], '%Y-%m-%dT%H:%M:%S')
        orders_datetime = orders_datetime.date()
        if (orders_datetime < cut_off_date):
            items_collection.remove(item)

    item_id = orders_collection.find_one()['_id']
    db.orders_json.update_one({'_id':ObjectId(item_id)}, {'$set':{'items':items_collection}})
    logging.info('Time taken to clear orders data in MongoDB - {}'.format(time.time() - orders_clean_time))

schedule.every(Labs_ExtractionFrequency).minutes.do(run_threaded, dump_labs_json_data)
schedule.every(Meds_ExtractionFrequency).minutes.do(run_threaded, dump_meds_json_data)
schedule.every(Orders_ExtractionFrequency).minutes.do(run_threaded, dump_orders_json_data)

schedule.every(1).day.at("23:59").do(run_threaded, clean_labs_collection)
schedule.every(1).day.at("23:59").do(run_threaded, clean_meds_collection)
schedule.every(1).day.at("23:59").do(run_threaded, clean_orders_collection)

# Parse json file in python
def extract_labs_data(labs_user_query=None):
    labs_collection = db.labs_json
    labs_cursor = labs_collection.find({})
    for document in labs_cursor:
        labs_data = document

    list_dict = []
    if (labs_user_query):
        required_columns = labs_user_query
    else:
        required_columns = labs_data['items'].keys()

    for i in range(len(labs_data['items'])):
        list_dict.append(labs_data['items'][i])

    labs_df = pd.DataFrame(list_dict)
    labs_df = labs_df[required_columns]
    return (labs_df.head())

def extract_meds_data(meds_user_query):
    meds_collection = db.meds_json
    meds_cursor = meds_collection.find({})
    for document in meds_cursor:
        meds_data = document

    list_dict = []
    if (meds_user_query):
        required_columns = meds_user_query
    else:
        required_columns = meds_data['items'].keys()

    for i in range(len(meds_data['items'])):
        list_dict.append(meds_data['items'][i])

    meds_df = pd.DataFrame(list_dict)
    meds_df = meds_df[required_columns]
    return (meds_df.head())

def extract_orders_data(orders_user_query):
    orders_collection = db.orders_json
    orders_cursor = orders_collection.find({})
    for document in orders_cursor:
        orders_data = document

    list_dict = []
    if (orders_user_query):
        required_columns = orders_user_query
    else:
        required_columns = orders_data['items'].keys()

    for i in range(len(orders_data['items'])):
        list_dict.append(orders_data['items'][i])

    orders_df = pd.DataFrame(list_dict)
    orders_df = orders_df[required_columns]
    return (orders_df.head())

extract_labs_data(labs_user_query=['empi', 'lab', 'result_val'])

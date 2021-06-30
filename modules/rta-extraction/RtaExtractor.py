#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
from pymongo import MongoClient

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
try:
    client = MongoClient(Mongo_URI)
    logging.info('MongoDB Connection Successful.')
except:
    logging.info('MongoDB Connection Unsuccessful.')

db = client.database

def dump_labs_json_data():
    labs_collection = db.labs_json
    for file in os.listdir(Labs_FolderPath):
        if file.endswith('.json'):
            Labs_FilePath = Labs_FolderPath+file

    f = open(Labs_FilePath, 'r')
    labs_data = json.load(f)
    labs_collection.insert_one(labs_data)
    f.close()

    logging.info('Labs data is dumped into MongoDB. The collection name is - labs_json')
    return (labs_collection, labs_data)

def dump_meds_json_data():
    meds_collection = db.meds_json
    for file in os.listdir(Meds_FolderPath):
        if file.endswith('.json'):
            Meds_FilePath = Meds_FolderPath+file

    f = open(Meds_FilePath, 'r')
    meds_data = json.load(f)
    meds_collection.insert_one(meds_data)
    f.close()

    logging.info('Meds data is dumped into MongoDB. The collection name is - meds_json')
    return (meds_collection, meds_data)

def dump_orders_json_data():
    orders_collection = db.orders_json
    for file in os.listdir(Orders_FolderPath):
        if file.endswith('.json'):
            Orders_FilePath = Orders_FolderPath+file

    f = open(Orders_FilePath, 'r')
    orders_data = json.load(f)
    orders_collection.insert_one(orders_data)
    f.close()

    logging.info('Orders data is dumped into MongoDB. The collection name is - orders_json')
    return (orders_collection, orders_data)

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

schedule.every(Labs_ExtractionFrequency).minutes.do(run_threaded, dump_labs_json_data)
schedule.every(Meds_ExtractionFrequency).minutes.do(run_threaded, dump_meds_json_data)
schedule.every(Orders_ExtractionFrequency).minutes.do(run_threaded, dump_orders_json_data)

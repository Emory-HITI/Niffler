import logging
import pickle5 as pickle
import json

with open('config.json', 'r') as f:
    config = json.load(f)

# Get variables for the each on-demand extraction from config.json
csv_file = config['CsvFile']


niffler_log = csv_file  + 'progresss.csv'

logging.basicConfig(filename=niffler_log,level=logging.INFO, format='%(message)s')

# Variables to track progress between iterations.
extracted_ones = list()

with open(csv_file +'.pickle', 'rb') as f:
    extracted_ones = pickle.load(f)
    for i in extracted_ones:
        logging.info(i.replace("_", ", "))

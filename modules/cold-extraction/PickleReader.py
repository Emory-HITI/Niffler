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

# By default, assume that this is a fresh extraction.
resume = False

# All extracted files from the csv file are saved in a respective .pickle file.

with open(csv_file +'.pickle', 'rb') as f:
    extracted_ones = pickle.load(f)
    wrap_start = '['
    wrap_end = ']'
    # temp = extracted_ones.partition(wrap_start)[2] 
    # output = temp.partition(wrap_end)[1]
    for i in extracted_ones:
        logging.info(i.replace("_", ", "))

    # Since we have successfully located a pickle file, it indicates that this is a resume.

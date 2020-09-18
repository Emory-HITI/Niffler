import logging
import os
import signal
import csv
import time
import shutil
import subprocess
import datetime
import json

logging.basicConfig(filename='niffler.log',level=logging.INFO)

with open('system.json', 'r') as f:
    niffler = json.load(f)

with open('config.json', 'r') as f:
    config = json.load(f)


#Get variables for StoreScp from config.json.
storage_folder = config['StorageFolder']
file_path = config['FilePath']

# Get variables for the each on-demand extraction from config.json
csv_file = config['CsvFile']
extraction_type = config['ExtractionType']
accession_index = config['AccessionIndex']
patient_index = config['PatientIndex']
date_index = config['DateIndex']
date_type = config['DateType']
date_format = config['DateFormat']

# Get constants from system.json
DCM4CHE_BIN = niffler['DCM4CHEBin']
SRC_AET = niffler['SrcAet']
QUERY_AET = niffler['QueryAet']
DEST_AET = niffler['DestAet']

accessions = []
patients = []
dates = []

# record the start time
t_start = time.time()

# Kill the previous storescp process.
check_kill_process('storescp')

pid = subprocess.call("{0} --accept-unknown --directory {1} --filepath {2} -b {3}".format(DCM4CHE_BIN, storage_folder, file_path, QUERY_AET), shell=True)

with open(csv_file, newline='') as f:
    reader = csv.reader(f)
    next(f)
    for row in reader:
        if (extraction_type == 'empi_date'):
            patients.append(row[patient_index])
            temp_date = row[date_index]
            dt_stamp = datetime.datetime.strptime(temp_date, date_format)
            date_str = dt_stamp.strftime('%Y%m%d')
            dates.append(date_str)
            length = len(patients)
        elif (extraction_type == 'accession'):
            accessions.append(row[accession_index])
            length = len(accessions)
        elif (extraction_type == 'empi_accession'):
            patients.append(row[patient_index])
            accessions.append(row[accession_index])
            length = len(accessions)


# For the cases that have the typical EMPI and Accession values together.
if (extraction_type == 'empi_accession'):
    # Create our Identifier (query) dataset
    for pid in range(0, len(patients)):
        Accession = accessions[pid]
        PatientID = patients[pid]
        subprocess.call("{0}/movescu -c {1} -b {2} -M PatientRoot -m PatientID={3} -m AccessionNumber={4} --dest {5}".format(DCM4CHE_BIN, SRC_AET, QUERY_AET, PatientID, Accession, DEST_AET), shell=True)

# For the cases that does not have the typical EMPI and Accession values together.
elif (extraction_type == 'empi_date' or extraction_type == 'accession'):
 
    # Create our Identifier (query) dataset
    for pid in range(0, length):
        if (extraction_type == 'empi_date'):
            Date = dates[pid]
            PatientID = patients[pid]
            subprocess.call("{0}/findscu -c {1} -b {2} -m PatientID={3} -m {4}={5}  -r StudyInstanceUID -x stid.csv.xsl --out-cat --out-file intermediate.csv --out-dir .".format(DCM4CHE_BIN, SRC_AET, QUERY_AET, PatientID, date_type, Date), shell=True)
        elif (extraction_type == 'accession'):
            Accession = accessions[pid]
            subprocess.call("{0}/findscu -c {1} -b {2} -m AccessionNumber={3} -r PatientID  -r StudyInstanceUID -x stid.csv.xsl --out-cat --out-file intermediate.csv --out-dir .".format(DCM4CHE_BIN, SRC_AET, QUERY_AET, Accession), shell=True)

        #Processing the Intermediate CSV file with EMPI and StudyIDs
        with open('intermediate1.csv', newline='') as g: #DCM4CHE appends 1.
            reader2 = csv.reader(g)
            # Array of studies
            patients2 = []
            studies2 = []
            for row2 in reader2:
                patients2.append(row2[1])
                studies2.append(row2[0])
 
        # Create our Identifier (query) dataset
        for pid2 in range(0, len(patients2)):
            Study = studies2[pid2]
            Patient = patients2[pid2]
            subprocess.call("{0}/movescu -c {1} -b {2} -M PatientRoot -m PatientID={3} -m StudyInstanceUID={4} --dest {5}".format(DCM4CHE_BIN, SRC_AET, QUERY_AET, Patient, Study, DEST_AET), shell=True)
 
# Record the total run-time
logging.info('Total run time: %s %s', time.time() - t_start, ' seconds!')



def check_kill_process(pstring):
    for line in os.popen("ps ax | grep " + pstring + " | grep -v grep"):
        fields = line.split()
        pid = fields[0]
        logging.info('killing previous storescp process')
        os.kill(int(pid), signal.SIGKILL)
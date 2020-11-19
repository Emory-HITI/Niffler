import logging
import os
import signal
import csv
import time
import shutil
import subprocess
import datetime
import json
import sys
import schedule
import pickle
import threading


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
NIGHTLY_ONLY = niffler['NightlyOnly']
START_HOUR = niffler['StartHour']
END_HOUR = niffler['EndHour']
IS_EXTRACTION_NOT_RUNNING = True


accessions = []
patients = []
dates = []

storescp_processes = 0
niffler_processes = 0

nifflerscp_str = "storescp.*{0}".format(QUERY_AET)
qbniffler_str = 'ColdDataRetriever'

# Variables to track progress between iterations.
extracted_ones = list()

# By default, assume that this is a fresh extraction.
resume = False

# All extracted files from the csv file are saved in a respective .pickle file.
try:
    with open(csv_file +'.pickle', 'rb') as f:
        extracted_ones = pickle.load(f)
        # Since we have successfully located a pickle file, it indicates that this is a resume.
        resume = True
except:
    logging.info("Unable to load a valid pickle file. Initialized with empty value to track the extracted ones in {0}.pickle.".format(csv_file))

# record the start time
t_start = time.time()

def check_kill_process():
    for line in os.popen("ps ax | grep -E " + nifflerscp_str + " | grep -v grep"):
        fields = line.split()
        pid = fields[0]
        logging.info("[EXTRACTION COMPLETE] {0}: Niffler Extraction to {1} Completes. Terminating the completed storescp process.".format(datetime.datetime.now(), storage_folder))
        os.kill(int(pid), signal.SIGKILL)


def sanity_check():
    global niffler_processes
    global storescp_processes
    for line in os.popen("ps ax | grep " + qbniffler_str + " | grep -v grep"):
        niffler_processes += 1
    for line in os.popen("ps ax | grep -E " + nifflerscp_str + " | grep -v grep"):
        storescp_processes += 1

    logging.info("Number of running niffler processes: {0} and storescp processes: {1}".format(niffler_processes, storescp_processes))

    if niffler_processes > 1:
        logging.error("[EXTRACTION FAILURE] {0}: Previous extraction still running. As such, your extraction attempt was not suuccessful this time. Please wait until that completes and re-run your query.".format(datetime.datetime.now()))
        sys.exit(0)

    if storescp_processes >= niffler_processes:
        logging.info('Killing the idling storescp processes')       
        check_kill_process()

    logging.info("{0}: StoreScp process for the current Niffler extraction will be started next".format(datetime.datetime.now()))


sanity_check()


subprocess.call("{0}/storescp --accept-unknown --directory {1} --filepath {2} -b {3} > storescp.out &".format(DCM4CHE_BIN, storage_folder, file_path, QUERY_AET), shell=True)




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


# Run the retrieval only once, when the extraction script starts, and keep it running in a separate thread.
def run_retrieval():
    global IS_EXTRACTION_NOT_RUNNING
    if IS_EXTRACTION_NOT_RUNNING:
        IS_EXTRACTION_NOT_RUNNING = False   
        logging.info('Starting the extractions...')
        retrieve()


# The core DICOM on-demand retrieve process.
def retrieve():
    # For the cases that have the typical EMPI and Accession values together.
    if (extraction_type == 'empi_accession'):
        # Create our Identifier (query) dataset
        for pid in range(0, len(patients)):
            Accession = accessions[pid]
            PatientID = patients[pid]
            temp_id = PatientID + '_' + Accession
            if (NIGHTLY_ONLY == 'True'):
                current_hour = datetime.datetime.now().hour
                while (current_hour >= int(END_HOUR) and current_hour < int(START_HOUR)):
                    # SLEEP FOR 30 minutes
                    time.sleep(30)
                    logging.info("Nightly mode. Niffler schedules the extraction to resume at start hour {0} and start within 30 minutes after that. It will then pause at the end hour {1}".format(START_HOUR, END_HOUR))
            if ((not resume) or (resume and (temp_id.decode("utf-8") not in extracted_ones))):
                subprocess.call("{0}/movescu -c {1} -b {2} -M PatientRoot -m PatientID={3} -m AccessionNumber={4} --dest {5}".format(DCM4CHE_BIN, SRC_AET, QUERY_AET, PatientID, Accession, DEST_AET), shell=True)
                extracted_ones.append(temp_id)

    # For the cases that does not have the typical EMPI and Accession values together.
    elif (extraction_type == 'empi_date' or extraction_type == 'accession'):
        # Create our Identifier (query) dataset
        for pid in range(0, length):
            if (NIGHTLY_ONLY == 'True'):
                current_hour = datetime.datetime.now().hour
                while (current_hour >= int(END_HOUR) and current_hour < int(START_HOUR)):
                    # SLEEP FOR 30 minutes
                    time.sleep(30)
                    logging.info("Nightly mode. Niffler schedules the extraction to resume at start hour {0} and start within 30 minutes after that. It will then pause at the end hour {1}".format(START_HOUR, END_HOUR))

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
                temp_id = Patient + '_' + Study
                if ((not resume) or (resume and (temp_id not in extracted_ones))):
                    subprocess.call("{0}/movescu -c {1} -b {2} -M PatientRoot -m PatientID={3} -m StudyInstanceUID={4} --dest {5}".format(DCM4CHE_BIN, SRC_AET, QUERY_AET, Patient, Study, DEST_AET), shell=True)
                    extracted_ones.append(temp_id)


 
# Record the total run-time
logging.info('Total run time: %s %s', time.time() - t_start, ' seconds!')


# Kill the running storescp process of QbNiffler.
check_kill_process()


# Write the pickle file periodically to track the progress and persist it to the filesystem
def update_pickle():
    global extracted_ones
    # Pickle using the highest protocol available.
    with open(csv_file +'.pickle', 'wb') as f:
        pickle.dump(extracted_ones, f, pickle.HIGHEST_PROTOCOL)
    logging.debug('dumping complete')


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()
    

# The thread scheduling
schedule.every(1).minutes.do(run_threaded, run_retrieval)    
schedule.every(2).minutes.do(run_threaded, update_pickle)

# Keep running in a loop.
while True:
    schedule.run_pending()
    time.sleep(1)

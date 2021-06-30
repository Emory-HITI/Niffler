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
import argparse

from collections import defaultdict

# MAKING ALL VARIABLES GLOBAL !!
# Add logging.shutdown() upon graceful completion

# def read_csv(csv_file):
#     upload_folder = '../frontend/uploads/csv/' + csv_file # Change the storage folder path
#     print("--------- READING CSV FILE ---------")
#     with open(upload_folder, newline='') as f:
#         reader = csv.reader(f)
#         next(f)
#         for row in reader:
#             print(row)

def initialize_Values(valuesDict):
    global storescp_processes, niffler_processes, nifflerscp_str, qbniffler_str
    global storage_folder, file_path, csv_file, extraction_type, accession_index, patient_index, date_index, date_type, date_format, email, send_email
    global DCM4CHE_BIN, SRC_AET, QUERY_AET, DEST_AET, NIGHTLY_ONLY, START_HOUR, END_HOUR, IS_EXTRACTION_NOT_RUNNING, NIFFLER_ID, MAX_PROCESSES, SEPARATOR
    global accessions, patients, dates, niffler_log, resume

    storage_folder = valuesDict['storage_folder']
    file_path = valuesDict['file_path']
    csv_file = valuesDict['CsvFile']
    extraction_type = valuesDict['extraction_type']
    accession_index = int(valuesDict['accession_index'])
    patient_index = int(valuesDict['patient_index'])
    date_index = int(valuesDict['date_index'])
    date_type = valuesDict['date_type']
    date_format = valuesDict['date_format']
    email = valuesDict['email']
    send_email = bool(valuesDict['send_email'])

    # Reads the system_json file.
    # system_json = 'modules/cold-extraction/system.json'
    with open('../cold-extraction/system.json', 'r') as f:
        niffler = json.load(f)

    # Get constants from system.json
    DCM4CHE_BIN = niffler['DCM4CHEBin']
    SRC_AET = niffler['SrcAet']
    QUERY_AET = niffler['QueryAet']
    DEST_AET = niffler['DestAet']
    NIGHTLY_ONLY = niffler['NightlyOnly']
    START_HOUR = niffler['StartHour']
    END_HOUR = niffler['EndHour']
    IS_EXTRACTION_NOT_RUNNING = True
    NIFFLER_ID = niffler['NifflerID']
    MAX_PROCESSES = niffler['MaxNifflerProcesses']

    SEPARATOR = ','

    accessions = []
    patients = []
    dates = []

    storescp_processes = 0
    niffler_processes = 0

    nifflerscp_str = "storescp.*{0}".format(QUERY_AET)
    qbniffler_str = 'ColdDataRetriever'

    niffler_log = 'niffler' + str(NIFFLER_ID) + '.log'

    logging.basicConfig(filename=niffler_log,level=logging.INFO)
    logging.getLogger('schedule').setLevel(logging.WARNING)

    # Variables to track progress between iterations.
    global extracted_ones
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
        logging.info("No existing pickle file found. Therefore, initialized with empty value to track the progress to {0}.pickle.".format(csv_file))

    # record the start time
    t_start = time.time()
    run_cold_extraction()

# Check and kill the StoreScp processes.
def check_kill_process():
    for line in os.popen("ps ax | grep -E " + nifflerscp_str + " | grep -v grep"):
        fields = line.split()
        pid = fields[0]
        logging.info("[EXTRACTION COMPLETE] {0}: Niffler Extraction to {1} Completes. Terminating the completed storescp process.".format(datetime.datetime.now(), storage_folder))
        try:
            os.kill(int(pid), signal.SIGKILL)
        except PermissionError:
            logging.warning("The previous user's StoreScp process has become an orphan. It is roaming around freely, like a zombie. Please kill it first")
            logging.warning("From your terminal run the below commands.")
            logging.warning("First find the pid of the storescp:- sudo ps -xa | grep storescp")
            logging.warning("Then kill that above process with:- sudo kill -9 PID-FROM-THE-PREVIOUS-STEP")
            logging.warning("Once killed, restart Niffler as before.")
            logging.error("Your current Niffler process terminates now. You or someone with sudo privilege must kill the idling storescp process first...")
            sys.exit(1)                


# Initialize the storescp and Niffler AET.
def initialize():
    global niffler_processes
    global storescp_processes
    print(niffler_processes, storescp_processes, MAX_PROCESSES)
    for line in os.popen("ps ax | grep " + qbniffler_str + " | grep -v grep"):
        niffler_processes += 1
    for line in os.popen("ps ax | grep -E " + nifflerscp_str + " | grep -v grep"):
        storescp_processes += 1

    logging.info("Number of running niffler processes: {0} and storescp processes: {1}".format(niffler_processes, storescp_processes))

    if niffler_processes > MAX_PROCESSES:
        logging.error("[EXTRACTION FAILURE] {0}: Previous {1} extractions still running. As such, your extraction attempt was not successful this time. Please wait until those complete and re-run your query.".format(datetime.datetime.now(), MAX_PROCESSES))
        #sys.exit(0)

    if storescp_processes >= niffler_processes:
        logging.info('Killing the idling storescp processes')       
        #check_kill_process()

    logging.info("{0}: StoreScp process for the current Niffler extraction is starting now".format(datetime.datetime.now()))

    subprocess.call("{0}/storescp --accept-unknown --directory {1} --filepath {2} -b {3} > storescp.out &".format(DCM4CHE_BIN, storage_folder, file_path, QUERY_AET), shell=True)


def read_csv():
    upload_folder = '../frontend/uploads/csv/' + csv_file # Change the storage folder path
    with open(upload_folder, newline='') as f:
        reader = csv.reader(f)
        next(f)
        for row in reader:
            row = [x.strip() for x in row]
            if (extraction_type == 'empi_date'):
                if not ((row[patient_index] == "") or (row[date_index] == "")):
                    patients.append(row[patient_index])
                    temp_date = row[date_index]
                    dt_stamp = datetime.datetime.strptime(temp_date, date_format)
                    date_str = dt_stamp.strftime('%Y%m%d')
                    dates.append(date_str)
                    length = len(patients)
            elif (extraction_type == 'empi'):
                if not ((row[patient_index] == "")):
                    patients.append(row[patient_index])
                    length = len(patients)
            elif (extraction_type == 'accession'):
                if not ((row[accession_index] == "")):
                    accessions.append(row[accession_index])
                    length = len(accessions)
            elif (extraction_type == 'empi_accession'):
                if not ((row[patient_index] == "") or (row[accession_index] == "")):
                    patients.append(row[patient_index])
                    accessions.append(row[accession_index])
                    length = len(accessions)


# Run the retrieval only once, when the extraction script starts, and keep it running in a separate thread.
def run_retrieval():
    global IS_EXTRACTION_NOT_RUNNING
    print("In run_retrieval:", IS_EXTRACTION_NOT_RUNNING)
    if IS_EXTRACTION_NOT_RUNNING:
        IS_EXTRACTION_NOT_RUNNING = False   
        logging.info('Starting the extractions...')
        initialize()
        retrieve()


# The core DICOM on-demand retrieve process.
def retrieve():
    # For the cases that have the typical EMPI and Accession values together.
    if (extraction_type == 'empi_accession'):
        # Create our Identifier (query) dataset
        for pid in range(0, len(patients)):
            Accession = accessions[pid]
            PatientID = patients[pid]
            temp_id = PatientID + SEPARATOR + Accession
            if NIGHTLY_ONLY:
                if (datetime.datetime.now().hour >= END_HOUR and datetime.datetime.now().hour < START_HOUR):
                    # log once while sleeping
                    logging.info("Nightly mode. Niffler schedules the extraction to resume at start hour {0} and start within 30 minutes after that. It will then pause at the end hour {1}".format(START_HOUR, END_HOUR))
                while (datetime.datetime.now().hour >= END_HOUR and datetime.datetime.now().hour < START_HOUR):
                    #sleep for 5 minutes
                    time.sleep(300)
            if ((not resume) or (resume and (temp_id not in extracted_ones))):
                subprocess.call("{0}/movescu -c {1} -b {2} -M PatientRoot -m PatientID={3} -m AccessionNumber={4} --dest {5}".format(DCM4CHE_BIN, SRC_AET, QUERY_AET, PatientID, Accession, DEST_AET), shell=True)
                extracted_ones.append(temp_id)

    # For the cases that have the EMPI.
    elif (extraction_type == 'empi'):
        # Create our Identifier (query) dataset
        for pid in range(0, len(patients)):
            PatientID = patients[pid]
            if NIGHTLY_ONLY:
                if (datetime.datetime.now().hour >= END_HOUR and datetime.datetime.now().hour < START_HOUR):
                    # log once while sleeping
                    logging.info("Nightly mode. Niffler schedules the extraction to resume at start hour {0} and start within 30 minutes after that. It will then pause at the end hour {1}".format(START_HOUR, END_HOUR))
                while (datetime.datetime.now().hour >= END_HOUR and datetime.datetime.now().hour < START_HOUR):
                    # sleep for 5 minutes
                    time.sleep(300)
            if ((not resume) or (resume and (PatientID not in extracted_ones))):
                subprocess.call("{0}/movescu -c {1} -b {2} -M PatientRoot -m PatientID={3} --dest {4}".format(DCM4CHE_BIN, SRC_AET, QUERY_AET, PatientID, DEST_AET), shell=True)
                extracted_ones.append(PatientID)

    # For the cases that does not have the typical EMPI and Accession values together.
    elif (extraction_type == 'empi_date' or extraction_type == 'accession'):
        # Create our Identifier (query) dataset
        for pid in range(0, length):
            if NIGHTLY_ONLY:
                if (datetime.datetime.now().hour >= END_HOUR and datetime.datetime.now().hour < START_HOUR):
                    # log once while sleeping
                    logging.info("Nightly mode. Niffler schedules the extraction to resume at start hour {0} and start within 30 minutes after that. It will then pause at the end hour {1}".format(START_HOUR, END_HOUR))
                while (datetime.datetime.now().hour >= END_HOUR and datetime.datetime.now().hour < START_HOUR):
                    #sleep for 5 minutes
                    time.sleep(300)
            if (extraction_type == 'empi_date'):
                Date = dates[pid]
                PatientID = patients[pid]
                subprocess.call("{0}/findscu -c {1} -b {2} -m PatientID={3} -m {4}={5}  -r StudyInstanceUID -x stid.csv.xsl --out-cat --out-file intermediate.csv --out-dir .".format(DCM4CHE_BIN, SRC_AET, QUERY_AET, PatientID, date_type, Date), shell=True)
            elif (extraction_type == 'accession'):
                Accession = accessions[pid]
                subprocess.call("{0}/findscu -c {1} -b {2} -m AccessionNumber={3} -r PatientID  -r StudyInstanceUID -x stid.csv.xsl --out-cat --out-file intermediate.csv --out-dir .".format(DCM4CHE_BIN, SRC_AET, QUERY_AET, Accession), shell=True)

            try:
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
                    temp_id = Patient + SEPARATOR + Study
                    if ((not resume) or (resume and (temp_id not in extracted_ones))):
                        subprocess.call("{0}/movescu -c {1} -b {2} -M PatientRoot -m PatientID={3} -m StudyInstanceUID={4} --dest {5}".format(DCM4CHE_BIN, SRC_AET, QUERY_AET, Patient, Study, DEST_AET), shell=True)
                        extracted_ones.append(temp_id)
                        
            except IOError:
                logging.info("No EMPI, StudyInstanceUID found for the current entry. Skipping this line, and moving to the next")


    # Kill the running storescp process of QbNiffler.
    check_kill_process() 

    if send_email:
        subprocess.call('echo "Niffler has successfully completed the DICOM retrieval" | mail -s "The DICOM retrieval has been complete" {0}'.format(email), shell=True)

    # Record the total run-time
    logging.info('Total run time: %s %s', time.time() - t_start, ' seconds!')

    #Extraction has successfully completed.
    os.kill(os.getpid(), signal.SIGINT)


# Write the pickle file periodically to track the progress and persist it to the filesystem
def update_pickle():
    print("In update_pickle")
    global extracted_ones
    # Pickle using the highest protocol available.
    with open(csv_file +'.pickle', 'wb') as f:
        pickle.dump(extracted_ones, f)
    logging.debug('Progress is recorded to the pickle file')


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()
    
def run_cold_extraction():
    print("In run_cold_extraction")
    read_csv()
    # The thread scheduling
    schedule.every(1).minutes.do(run_threaded, run_retrieval)    
    schedule.every(10).minutes.do(run_threaded, update_pickle)

    # # Keep running in a loop.
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            check_kill_process()
            logging.shutdown()
            sys.exit(0)

if __name__ == "__main__":
    global storescp_processes, niffler_processes, nifflerscp_str, qbniffler_str
    global storage_folder, file_path, csv_file, extraction_type, accession_index, patient_index, date_index, date_type, date_format, email, send_email
    global DCM4CHE_BIN, SRC_AET, QUERY_AET, DEST_AET, NIGHTLY_ONLY, START_HOUR, END_HOUR, IS_EXTRACTION_NOT_RUNNING, NIFFLER_ID, MAX_PROCESSES, SEPARATOR
    global accessions, patients, dates, niffler_log, resume

    config = defaultdict(lambda: None)
    # Read Default config.json file
    with open('config.json', 'r') as f:
        tmp_config = json.load(f)
        config.update(tmp_config)

    # CLI Argument Parser
    ap = argparse.ArgumentParser()

    ap.add_argument("--NifflerSystem", default=config['NifflerSystem'],
                    help="Path to json file with Niffler System Information.")
    ap.add_argument("--StorageFolder",
                    default=config['StorageFolder'], help="StoreSCP config: Storage Folder. Refer Readme.md")
    ap.add_argument("--FilePath", default=config['FilePath'],
                    help="StoreSCP config: FilePath, Refer configuring config.json in Readme.md.")
    ap.add_argument("--CsvFile", default=config['CsvFile'],
                    help="Path to CSV file for extraction. Refer Readme.md.")
    ap.add_argument("--ExtractionType", default=config['ExtractionType'],
                    help="One of the supported extraction type for Cold Data extraction. Refer Readme.md.")
    ap.add_argument("--AccessionIndex", default=config['AccessionIndex'], type=int,
                    help="Set the CSV column index of AccessionNumber for extractions with Accessions.")
    ap.add_argument("--PatientIndex", default=config['PatientIndex'], type=int,
                    help="Set the CSV column index of EMPI for extractions with EMPI and an accession or EMPI and a date.")
    ap.add_argument("--DateIndex", default=config['DateIndex'], type=int,
                    help="Set the CSV column index of Date(StudyDate, AcquisitionDate) for extractions with EMPI and a date.")
    ap.add_argument("--DateType", default=config['DateType'],
                    help="DateType can range from AcquisitionDate, StudyDate, etc. Refer Readme.md.")
    ap.add_argument("--DateFormat", default=config['DateFormat'],
                    help="DateFormat can range from %Y%m%d, %m/%d/%y, %m-%d-%y, %%m%d%y, etc. Refer Readme.md.")
    ap.add_argument("--SendEmail", default=config['SendEmail'], type=bool,
                    help="Send email when extraction is complete. Default false")
    ap.add_argument("--YourEmail", default=config['YourEmail'],
                    help="A valid email, if send email is enabled.")

    args = vars(ap.parse_args())

    #Get variables for StoreScp from config.json.
    storage_folder = args['StorageFolder']
    file_path = args['FilePath']

    # Get variables for the each on-demand extraction from config.json
    csv_file = args['CsvFile']
    extraction_type = args['ExtractionType']
    accession_index = args['AccessionIndex']
    patient_index = args['PatientIndex']
    date_index = args['DateIndex']
    date_type = args['DateType']
    date_format = args['DateFormat']
    email = args['YourEmail']
    send_email = args['SendEmail']

    # Reads the system_json file.
    system_json = args['NifflerSystem']

    with open(system_json, 'r') as f:
        niffler = json.load(f)

    # Get constants from system.json
    DCM4CHE_BIN = niffler['DCM4CHEBin']
    SRC_AET = niffler['SrcAet']
    QUERY_AET = niffler['QueryAet']
    DEST_AET = niffler['DestAet']
    NIGHTLY_ONLY = niffler['NightlyOnly']
    START_HOUR = niffler['StartHour']
    END_HOUR = niffler['EndHour']
    IS_EXTRACTION_NOT_RUNNING = True
    NIFFLER_ID = niffler['NifflerID']
    MAX_PROCESSES = niffler['MaxNifflerProcesses']

    SEPARATOR = ','

    accessions = []
    patients = []
    dates = []

    storescp_processes = 0
    niffler_processes = 0

    nifflerscp_str = "storescp.*{0}".format(QUERY_AET)
    qbniffler_str = 'ColdDataRetriever'

    niffler_log = 'niffler' + str(NIFFLER_ID) + '.log'

    logging.basicConfig(filename=niffler_log,level=logging.INFO)
    logging.getLogger('schedule').setLevel(logging.WARNING)

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
        logging.info("No existing pickle file found. Therefore, initialized with empty value to track the progress to {0}.pickle.".format(csv_file))

    # record the start time
    t_start = time.time()
    run_cold_extraction()

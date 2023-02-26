import logging
import os, glob
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
import random
import string
import itertools
import calendar
import pdb

import pandas as pd
import numpy as np
from collections import defaultdict


def initialize_config_and_execute(valuesDict):
    """
    Initializes the variables and starts the execution of the on-demand extraction.
    """
    global storescp_processes, niffler_processes, nifflerscp_str, niffler_str
    global storage_folder, file_path, csv_file, number_of_query_attributes, first_index, second_index, third_index, \
        first_attr, second_attr, third_attr, long_accession, date_format, email, send_email, system_json, mod_csv_file
    global DCM4CHE_BIN, SRC_AET, QUERY_AET, DEST_AET, NIGHTLY_ONLY, START_HOUR, END_HOUR, IS_EXTRACTION_NOT_RUNNING, \
        NIFFLER_ID, MAX_PROCESSES, SEPARATOR, cfind_add, out_folder
    global firsts, seconds, thirds, niffler_log, resume, length, t_start, cfind_only, cfind_detailed, temp_folder

    storage_folder = valuesDict['StorageFolder']
    file_path = valuesDict['FilePath']
    csv_file = valuesDict['CsvFile']
    number_of_query_attributes = int(valuesDict['NumberOfQueryAttributes'])
    first_index = int(valuesDict['FirstIndex'])
    second_index = int(valuesDict['SecondIndex'])
    third_index = int(valuesDict['ThirdIndex'])
    first_attr = valuesDict['FirstAttr']
    second_attr = valuesDict['SecondAttr']
    third_attr = valuesDict['ThirdAttr']
    long_accession = valuesDict['LongAccession']
    date_format = valuesDict['DateFormat']
    email = valuesDict['YourEmail']
    send_email = bool(valuesDict['SendEmail'])
    system_json = valuesDict['NifflerSystem']
    mod_csv_file = csv_file[:-4]+'_mod.csv'
    shutil.copyfile(csv_file, mod_csv_file)

    # Reads the system_json file.
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

    firsts = []
    seconds = []
    thirds = []

    storescp_processes = 0
    niffler_processes = 0

    nifflerscp_str = "storescp.*{0}".format(QUERY_AET)
    niffler_str = 'ColdDataRetriever'

    cfind_only = 'CFIND-ONLY'
    cfind_detailed = 'CFIND-DETAILED'

    temp_folder = os.path.join(storage_folder, "cfind-temp")

    if file_path == cfind_only:
        cfind_add = '-r StudyDescription -x description.csv.xsl'
        out_folder = temp_folder
    elif file_path == cfind_detailed:
        cfind_add = '-r StudyDescription -r StudyDate -r StudyTime -r DeviceSerialNumber ' \
                    '-r ProtocolName -r PerformedProcedureStepDescription -r NumberOfStudyRelatedSeries ' \
                    '-r NumberOfStudyRelatedInstances -r AcquisitionDate ' \
                    '-x detailed.csv.xsl'
        out_folder = temp_folder
    else:
        cfind_add = ' -x stid.csv.xsl '
        out_folder = '.'

    niffler_log = 'niffler' + str(NIFFLER_ID) + '.log'

    logging.basicConfig(filename=niffler_log, level=logging.INFO)
    logging.getLogger('schedule').setLevel(logging.WARNING)

    # Variables to track progress between iterations.
    global extracted_ones
    extracted_ones = list()

    # By default, assume that this is a fresh extraction.
    resume = False

    # All extracted files from the csv file are saved in a respective .pickle file.
    try:
        with open(mod_csv_file + '.pickle', 'rb') as f:
            extracted_ones = pickle.load(f)
            # Since we have successfully located a pickle file, it indicates that this is a resume.
            resume = True
    except:
        logging.info("No existing pickle file found. Therefore, initialized with empty value to track the progress to "
                     "{0}.pickle.".format(mod_csv_file))

    # record the start time
    t_start = time.time()
    run_cold_extraction()


def check_kill_process():
    """
    Check and kill the idling StoreScp processes.
    """
    for line in os.popen("ps ax | grep -E " + nifflerscp_str + " | grep -v grep"):
        fields = line.split()
        pid = fields[0]
        logging.info("[EXTRACTION COMPLETE] {0}: Niffler Extraction to {1} Completes. Terminating the completed "
                     "storescp process.".format(datetime.datetime.now(), storage_folder))
        try:
            os.kill(int(pid), signal.SIGKILL)
        except PermissionError:
            logging.warning("The previous user's StoreScp process has become an orphan. It is roaming around freely, "
                            "like a zombie. Please kill it first")
            logging.warning("From your terminal run the below commands.")
            logging.warning("First find the pid of the storescp:- sudo ps -xa | grep storescp")
            logging.warning("Then kill that above process with:- sudo kill -9 PID-FROM-THE-PREVIOUS-STEP")
            logging.warning("Once killed, restart Niffler as before.")
            logging.error("Your current Niffler process terminates now. You or someone with sudo privilege must kill "
                          "the idling storescp process first...")
            sys.exit(1)                


def initialize():
    """
    Initialize the storescp and Niffler AET.
    """                                                                          
    query_aet = QUERY_AET.split(":")[0]
    dest_aet = DEST_AET
    if query_aet == dest_aet:
        global niffler_processes
        global storescp_processes
        for _ in os.popen("ps ax | grep " + niffler_str + " | grep -v grep"):
            niffler_processes += 1
        for _ in os.popen("ps ax | grep -E " + nifflerscp_str + " | grep -v grep"):
            storescp_processes += 1

        logging.info("Number of running Niffler processes: {0} and storescp processes: {1}".format(niffler_processes,
                                                                                               storescp_processes))

        if niffler_processes > MAX_PROCESSES:
            logging.error("[EXTRACTION FAILURE] {0}: Previous {1} extractions still running. As such, your extraction "
                      "attempt was not successful this time. Please wait until those complete and re-run your"
                      " query.".format(datetime.datetime.now(), MAX_PROCESSES))
            sys.exit(0)

        if storescp_processes >= niffler_processes:
            logging.info('Killing the idling storescp processes')       
            check_kill_process()
  
        logging.info("{0}: StoreScp process for the current Niffler extraction is starting now".format(
            datetime.datetime.now()))

        if not file_path == cfind_only and not file_path == cfind_detailed:
            subprocess.call("{0}/storescp --accept-unknown --directory {1} --filepath {2} -b {3} > storescp.out &".format(
                DCM4CHE_BIN, storage_folder, file_path, QUERY_AET), shell=True)

    else:
        logging.info("{0}: This is an external AE. StoreScp will be started externally".format(datetime.datetime.now()))

def get_all_dates_given_month(string_val):
    date_format = '%Y%m'
    dt_stamp = datetime.datetime.strptime(string_val, date_format)
    month = dt_stamp.month
    year = dt_stamp.year
    no_of_days = calendar.monthrange(year, month)[1]
    first_date = datetime.date(year, month, 1)
    last_date = datetime.date(year, month, no_of_days)
    delta = last_date-first_date
    return (list(first_date+datetime.timedelta(days=i) for i in range(delta.days + 1)))

def create_mod_csv_file(csv_filepath):
    """
    Handles and converts StudyMonth attribute to StudyDate.
    """
    df = pd.read_csv(csv_filepath)
    if 'StudyMonth' in df.columns:
        for i in range(len(df)):
            df['StudyMonth'][i] = get_all_dates_given_month(str(df['StudyMonth'][i]))

        for i in range(len(df)):
            for col in df.columns:
                if col != 'StudyMonth':
                    df[col][i] = [str(df[col][i])] * len(df['StudyMonth'][i])

        mod_df = pd.DataFrame(columns=df.columns)
        for col in df.columns:
            sample_list = []
            sample_list.extend(df[col].values)
            sample_list = list(itertools.chain(*sample_list))
            mod_df[col] = sample_list

        mod_df['StudyMonth'] = pd.to_datetime(mod_df['StudyMonth'], format='%Y-%m-%d')
        mod_df = mod_df.rename(columns={'StudyMonth':'StudyDate'})
        return (mod_df)
    # To Do - Refactor the following code snippet without "for loop".
    if 'AccessionNumber' in df.columns:
        for i in range(len(df)):
            if (len(str(df['AccessionNumber'][i])) > 16) and long_accession:
                df['AccessionNumber'][i] = df['AccessionNumber'][i][0:7]+df['AccessionNumber'][i][9:]
        return (df)
    else:
        return (df)

def read_csv():
    """
    Read and parse the user provided csv file.
    """
    global length
    df = create_mod_csv_file(mod_csv_file)
    df.to_csv(mod_csv_file, index=False)
    with open(mod_csv_file, newline='') as f:
        reader = csv.reader(f)
        next(f)

        if number_of_query_attributes > 3 or number_of_query_attributes < 1:
            logging.info('Entered an invalid NumberOfQueryAttributes. Currently supported values, 1, 2, or 3. '
                         'Defaulting to 1 for this extraction')

        for row in reader:
            row = [x.strip() for x in row]

            if not (row[first_index] == ""):
                if first_attr == "StudyDate":
                    date_str = convert_to_date_format(row[first_index])
                    firsts.append(date_str)
                else:
                    firsts.append(row[first_index])

            if number_of_query_attributes == 2 or number_of_query_attributes == 3:
                if not (row[first_index] == "" or row[second_index] == ""):
                    if second_attr == "StudyDate":
                        date_str = convert_to_date_format(row[second_index])
                        seconds.append(date_str)
                    else:
                        seconds.append(row[second_index])

            if number_of_query_attributes == 3:
                if not (row[first_index] == "" or row[second_index] == "" or row[third_index] == ""):
                    if third_attr == "StudyDate":
                        date_str = convert_to_date_format(row[third_index])
                        thirds.append(date_str)
                    else:
                        thirds.append(row[third_index])

        length = max(len(firsts), len(seconds), len(thirds))
        logging.info("Issuing retrieval queries for the {0} number of entries in the csv file".format(length))


def convert_to_date_format(string_val):
    """
    Convert StudyDate value to the correct date format.
    """
    temp_date = string_val
    dt_stamp = datetime.datetime.strptime(temp_date, date_format)
    date_str = dt_stamp.strftime('%Y%m%d')
    return date_str

def run_retrieval():
    """
    Run the retrieval only once, when the extraction script starts, and keep it running in a separate thread.
    """
    global IS_EXTRACTION_NOT_RUNNING
    if IS_EXTRACTION_NOT_RUNNING:
        IS_EXTRACTION_NOT_RUNNING = False   
        logging.info('Starting the extractions...')
        initialize()
        retrieve()


def retrieve():
    """
    The core DICOM on-demand retrieve process to retrieve the images or metadata.
    """
    if file_path == cfind_only or file_path == cfind_detailed:
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)

    # Cases where only one DICOM keyword is considered as an attribute.
    if number_of_query_attributes > 3 or number_of_query_attributes <= 1:
        # For the cases that extract entirely based on the PatientID - Patient-level extraction.
        if first_attr == "PatientID":

            for pid in range(0, length):
                sleep_for_nightly_mode()
                patient = firsts[pid]
                if (not resume) or (resume and (patient not in extracted_ones)):
                    if file_path == cfind_only or file_path == cfind_detailed:
                        temp_file = generate_temp_file_name()
                        subprocess.call("{0}/findscu -c {1} -b {2} -M PatientRoot -m PatientID={3} -r AccessionNumber "
                                        "-r StudyInstanceUID {4} --out-cat --out-file {5} --out-dir {6}".format(
                            DCM4CHE_BIN, SRC_AET, QUERY_AET, patient, cfind_add, temp_file, out_folder), shell=True)
                    else:
                        subprocess.call("{0}/movescu -c {1} -b {2} -M PatientRoot -m PatientID={3} --dest {4}".format(
                            DCM4CHE_BIN, SRC_AET, QUERY_AET, patient, DEST_AET), shell=True)
                    extracted_ones.append(patient)
            merge_temp_files()

        # For the cases that extract based on a single property other than EMPI/PatientID. Goes to study level.
        # "Any" mode. Example: Extractions based on just AccessionNumber of AcquisitionDate.
        else:
            for pid in range(0, length):
                sleep_for_nightly_mode()
                first = firsts[pid]
                temp_file = generate_temp_file_name()
                subprocess.call("{0}/findscu -c {1} -b {2} -m {3}={4} -r PatientID -r StudyInstanceUID {5} "
                                " --out-cat --out-file {6} --out-dir {7}".format(
                    DCM4CHE_BIN, SRC_AET, QUERY_AET, first_attr, first, cfind_add, temp_file, out_folder), shell=True)
                if not (file_path == cfind_only or file_path == cfind_detailed):
                    extract_empi_study()
            merge_temp_files()

    # Cases where only two DICOM keywords are considered as attributes.
    elif number_of_query_attributes == 2:
        empi_accession_mode = False
        empi_study_mode = False
        patients = []
        accessions = []
        studies = []
        # For the typical case that has the PatientID and AccessionNumber values together.
        if first_attr == "PatientID" and second_attr == "AccessionNumber":
            empi_accession_mode = True
            patients = firsts
            accessions = seconds
        elif first_attr == "AccessionNumber" and second_attr == "PatientID":
            empi_accession_mode = True
            patients = seconds
            accessions = firsts
        # For the typical case that has the PatientID and StudyInstanceUID values together.
        elif first_attr == "PatientID" and second_attr == "StudyInstanceUID":
            empi_study_mode = True
            patients = firsts
            studies = seconds
        elif first_attr == "StudyInstanceUID" and second_attr == "PatientID":
            empi_study_mode = True
            patients = seconds
            studies = firsts

        if empi_accession_mode:
            for pid in range(0, length):
                sleep_for_nightly_mode()
                accession = accessions[pid]
                patient = patients[pid]
                temp_id = patient + SEPARATOR + accession
                if (not resume) or (resume and (temp_id not in extracted_ones)):
                    if file_path == cfind_only or file_path == cfind_detailed:
                        temp_file = generate_temp_file_name()
                        subprocess.call("{0}/findscu -c {1} -b {2} -M PatientRoot -m PatientID={3} "
                                        "-m AccessionNumber={4} -r StudyInstanceUID {5} --out-cat --out-file {6} "
                                        "--out-dir {7}".format(DCM4CHE_BIN, SRC_AET, QUERY_AET, patient, accession,
                                                             cfind_add, temp_file, out_folder), shell=True)
                    else:
                        subprocess.call("{0}/movescu -c {1} -b {2} -M PatientRoot -m PatientID={3} "
                                        "-m AccessionNumber={4} --dest {5}".format(DCM4CHE_BIN, SRC_AET, QUERY_AET,
                                                                                   patient, accession, DEST_AET), shell=True)
                    extracted_ones.append(temp_id)
            merge_temp_files()

        elif empi_study_mode:
            for pid in range(0, length):
                sleep_for_nightly_mode()
                study = studies[pid]
                patient = patients[pid]
                temp_id = patient + SEPARATOR + study
                if (not resume) or (resume and (temp_id not in extracted_ones)):
                    if file_path == cfind_only or file_path == cfind_detailed:
                        temp_file = generate_temp_file_name()
                        subprocess.call("{0}/findscu -c {1} -b {2} -M PatientRoot -m PatientID={3} "
                                        "-m StudyInstanceUID={4} -r AccessionNumber {5} --out-cat --out-file {6} "
                                        "--out-dir {7}".format(DCM4CHE_BIN, SRC_AET, QUERY_AET, patient, study,
                                                               cfind_add, temp_file, out_folder), shell=True)
                    else:
                        subprocess.call("{0}/movescu -c {1} -b {2} -m PatientID={3} -m StudyInstanceUID={4} "
                                        "--dest {5}".format(DCM4CHE_BIN, SRC_AET, QUERY_AET, patient, study,
                                                            DEST_AET), shell=True)
                    extracted_ones.append(temp_id)
            merge_temp_files()

        # For the cases that does not have the typical EMPI and Accession values together.
        # "Any, Any" mode. Example: empi and a date
        else:
            for pid in range(0, length):
                sleep_for_nightly_mode()
                first = firsts[pid]
                second = seconds[pid]
                temp_file = generate_temp_file_name()
                subprocess.call("{0}/findscu -c {1} -b {2} -m {3}={4} -m {5}={6} -r PatientID -r StudyInstanceUID {7} "
                                "--out-cat --out-file {8} --out-dir {9}".format(DCM4CHE_BIN, SRC_AET, QUERY_AET,
                                                                              first_attr, first, second_attr, second,
                                                                              cfind_add, temp_file, out_folder),
                                shell=True)
                if not (file_path == cfind_only or file_path == cfind_detailed):
                    extract_empi_study()
            merge_temp_files()

    # Cases where there DICOM keywords are considered as attributes. "Any, Any, Any" mode
    elif number_of_query_attributes == 3:
        for pid in range(0, length):
            sleep_for_nightly_mode()
            first = firsts[pid]
            second = seconds[pid]
            third = thirds[pid]
            temp_file = generate_temp_file_name()
            subprocess.call("{0}/findscu -c {1} -b {2} -m {3}={4} -m {5}={6} -m {7}={8} -r PatientID -r "
                            "StudyInstanceUID {9} --out-cat --out-file {10} --out-dir {11}".format(
                DCM4CHE_BIN, SRC_AET, QUERY_AET, first_attr, first, second_attr, second, third_attr, third, cfind_add,
                temp_file, out_folder), shell=True)
            if not (file_path == cfind_only or file_path == cfind_detailed):
                extract_empi_study()
        merge_temp_files()

    # Kill the running storescp process of Niffler.
    check_kill_process() 

    if send_email:
        subprocess.call('echo "Niffler has successfully completed the DICOM retrieval" | mail -s "The DICOM retrieval '
                        'has been complete" {0}'.format(email), shell=True)

    # Record the total run-time
    logging.info('Total run time: %s %s', time.time() - t_start, ' seconds!')

    # Extraction has successfully completed.
    os.kill(os.getpid(), signal.SIGINT)


def generate_temp_file_name():
    """
    Generate a name to generate a temporary file to store c-find outputs.
    """
    if file_path == cfind_only or file_path == cfind_detailed:
        inc = ''.join(random.choices(string.ascii_uppercase, k=10))
        temp_file = str(inc) + ".csv"
    else:
        temp_file = 'intermediate.csv'
    return temp_file


def merge_temp_files():
    """
    Merge temp files produced by c-find into the final output.
    Remove the temp folder created by c-find to produce intermediate files.
    """
    if os.path.exists('intermediate1.csv'):
        os.remove('intermediate1.csv')
    if file_path == cfind_only or file_path == cfind_detailed:
        all_filenames = [i for i in glob.glob(os.path.join(temp_folder, '*.*'))]
        with open(os.path.join(storage_folder, "cfind-output.csv"), 'w') as outfile:
            if file_path == cfind_only:
                init_line = "PatientID,StudyInstanceUID,AccessionNumber,StudyDescription\n"
            else:
                init_line = "PatientID,StudyInstanceUID,AccessionNumber,StudyDescription,StudyDate" \
                            "StudyTime,DeviceSerialNumber,ProtocolName,PerformedProcedureStepDescription," \
                            "NumberOfStudyRelatedSeries,NumberOfStudyRelatedInstances,AcquisitionDate\n"
            outfile.write(init_line)
            for fname in all_filenames:
                with open(fname) as infile:
                    for line in infile:
                        outfile.write(line)
        shutil.rmtree(temp_folder)


def extract_empi_study():
    """
    C-MOVE based on PatientID and StudyInstanceUID, executed by default for most cases after C-FIND.
    """
    try:
        # Processing the Intermediate CSV file with EMPI and StudyIDs
        with open('intermediate1.csv', newline='') as g:  # DCM4CHE appends 1.
            reader2 = csv.reader(g)
            # Array of studies
            patients2 = []
            studies2 = []
            for row2 in reader2:
                patients2.append(row2[1])
                studies2.append(row2[0])

        # Create our Identifier (query) dataset
        for pid2 in range(0, len(patients2)):
            study = studies2[pid2]
            patient = patients2[pid2]
            temp_id = patient + SEPARATOR + study
            if (not resume) or (resume and (temp_id not in extracted_ones)):
                subprocess.call("{0}/movescu -c {1} -b {2} -m PatientID={3} -m StudyInstanceUID={4} --dest {5}".
                                format(DCM4CHE_BIN, SRC_AET, QUERY_AET, patient, study, DEST_AET), shell=True)
                extracted_ones.append(temp_id)

    except IOError:
        logging.info("No EMPI, StudyInstanceUID found for the current entry. Skipping this line, and moving "
                     "to the next")


def sleep_for_nightly_mode():
    """
    Sleep during the day time if nightly mode is in place.
    """
    if NIGHTLY_ONLY:
        if END_HOUR <= datetime.datetime.now().hour < START_HOUR:
            # log once while sleeping
            logging.info("Nightly mode. Niffler schedules the extraction to resume at start hour {0} and "
                         "start within 30 minutes after that. It will then pause at the end hour {1}".format(
                START_HOUR, END_HOUR))
        while END_HOUR <= datetime.datetime.now().hour < START_HOUR:
            # sleep for 5 minutes
            time.sleep(300)


def update_pickle():
    """
    Write the pickle file periodically to track the progress and persist it to the filesystem.
    """
    with open(mod_csv_file + '.pickle', 'wb') as f:
        pickle.dump(extracted_ones, f)
    logging.debug('Progress is recorded to the pickle file')


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def run_cold_extraction():
    """
    Schedule the threads.
    """
    read_csv()
    # The thread scheduling
    schedule.every(1).minutes.do(run_threaded, run_retrieval)    
    schedule.every(10).minutes.do(run_threaded, update_pickle)

    # Keep running in a loop.
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            check_kill_process()
            logging.shutdown()
            sys.exit(0)


if __name__ == "__main__":
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
    ap.add_argument("--NumberOfQueryAttributes", default=config['NumberOfQueryAttributes'], type=int,
                    help="How many DICOM Attributes do you want to filter with for your retrieval. Default is 1.")
    ap.add_argument("--FirstAttr", default=config['FirstAttr'],
                    help="What is the first attribute you like to query with. Refer Readme.md.")
    ap.add_argument("--FirstIndex", default=config['FirstIndex'], type=int,
                    help="Set the CSV column index of the first query attribute.")
    ap.add_argument("--SecondAttr", default=config['SecondAttr'],
                    help="What is the second attribute you like to query with. Refer Readme.md. "
                         "Required only if the number of query attributes are 2 or 3")
    ap.add_argument("--SecondIndex", default=config['SecondIndex'], type=int,
                    help="Set the CSV column index of second query attribute. "
                         "Required only if the number of query attributes are 2 or 3")
    ap.add_argument("--ThirdAttr", default=config['ThirdAttr'],
                    help="What is the third attribute you like to query with. Refer Readme.md. "
                         "Required only if the number of query attributes is 3")
    ap.add_argument("--ThirdIndex", default=config['ThirdIndex'], type=int,
                    help="Set the CSV column index of third index query attribute. "
                         "Required only if the number of query attributes is 3")
    ap.add_argument("--LongAccession", default=config['LongAccession'], type=bool,
                    help="Allows Long Accession Numbers to be converted to default Acessions. Default true")
    ap.add_argument("--DateFormat", default=config['DateFormat'],
                    help="DateFormat can range from %Y%m%d, %m/%d/%y, %m-%d-%y, %%m%d%y, etc. Refer Readme.md.")
    ap.add_argument("--SendEmail", default=config['SendEmail'], type=bool,
                    help="Send email when extraction is complete. Default false")
    ap.add_argument("--YourEmail", default=config['YourEmail'],
                    help="A valid email, if send email is enabled.")

    args = vars(ap.parse_args())

    if len(args) > 0:
        initialize_config_and_execute(args)
    else:
        initialize_config_and_execute(config)

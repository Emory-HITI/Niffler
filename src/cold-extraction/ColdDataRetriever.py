import logging
import os
import csv
import time
import shutil
import subprocess
import datetime


logging.basicConfig(filename='niffler.log',level=logging.INFO)

DCM4CHE_BIN = "/opt/localdrive/dcm4che-5.19.0/bin"

# Enter the correct csv file name. Assumed to be in the current folder as this file. Otherwise, provide full path or relative path.
csvfile = "extractionCOVID2-YY.csv"

# Correct types: accession, empi_date
extraction_type = "accession"


# For extractions with Accessions only
accession_index = 0
accessions = []

# For extractions with EMPI and a date
patient_index = 1
date_index = 3
dateType = "StudyDate"
date_format = '%m/%d/%y'
patients = []
dates = []

# record the start time
t_start = time.time()
with open(csvfile, newline='') as f:
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

# Create our Identifier (query) dataset
for pid in range(0, length):
    if (extraction_type == 'empi_date'):
        Date = dates[pid]
        PatientID = patients[pid]

        subprocess.call("{0}/findscu -c AE_ARCH2@163.246.177.5:104 -b BMIPACS2:4243 -m PatientID={1} -m {2}={3}  -r StudyInstanceUID -x stid.csv.xsl --out-cat --out-file intermediate.csv --out-dir .".format(DCM4CHE_BIN,PatientID, dateType, Date), shell=True)
    elif (extraction_type == 'accession'):
        Accession = accessions[pid]

        subprocess.call("{0}/findscu -c AE_ARCH2@163.246.177.5:104 -b BMIPACS2:4243 -m AccessionNumber={1} -r PatientID  -r StudyInstanceUID -x stid.csv.xsl --out-cat --out-file intermediate.csv --out-dir .".format(DCM4CHE_BIN,Accession), shell=True)

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
        subprocess.call("{0}/movescu -c AE_ARCH2@163.246.177.5:104 -b BMIPACS2:4243 -M PatientRoot -m PatientID={1} -m StudyInstanceUID={2} --dest BMIPACS2".format(DCM4CHE_BIN,Patient, Study), shell=True)
 
# Record the total run-time
logging.info('Total run time: %s %s', time.time() - t_start, ' seconds!')

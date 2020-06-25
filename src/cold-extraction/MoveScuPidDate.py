import logging
import os
import csv
import time
import shutil
import subprocess

LOGGER = logging.getLogger('pynetdicom')
LOGGER.setLevel(logging.INFO)
DCM4CHE_BIN = "/opt/localdrive/dcm4che-5.19.0/bin"


csvfile = "DBS_modified.csv"
patient_index = 1
date_index = 2

# Array of accession numbers
patients = []
dates = []

# record the start time
t_start = time.time()

with open(csvfile, newline='') as f:
    reader = csv.reader(f)
    next(f)
    for row in reader:
        patients.append(row[patient_index])
        dates.append(row[date_index])



# Create our Identifier (query) dataset
for pid in range(0, len(patients)):
    Date = dates[pid]
    PatientID = patients[pid]

    subprocess.call("{0}/findscu -c AE_ARCH2@163.246.177.5:104 -b BMIPACS2:4243 -m PatientID={1} -m AcquisitionDate={2}  -r StudyInstanceUID -x stid.csv.xsl --out-cat --out-file imonintermediate.csv --out-dir .".format(DCM4CHE_BIN,PatientID, Date), shell=True)
    
    with open('imonintermediate1.csv', newline='') as g:
        reader2 = csv.reader(g)
        next(g)
    
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

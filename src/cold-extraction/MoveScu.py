import logging
import os
import csv
import time
import shutil
import subprocess

LOGGER = logging.getLogger('pynetdicom')
LOGGER.setLevel(logging.INFO)
DCM4CHE_BIN = "/opt/localdrive/dcm4che-5.19.0/bin"


csvfile = "progression_MG_screening_only_with_acc.csv"
patient_index = 0
accession_index = 1

# Array of accession numbers
patients = []
accessions = []

# record the start time
t_start = time.time()

with open(csvfile, newline='') as f:
    reader = csv.reader(f)
    next(f)
    for row in reader:
        patients.append(row[patient_index])
        accessions.append(row[accession_index])


os.chdir(DCM4CHE_BIN)

# Create our Identifier (query) dataset
for pid in range(0, len(patients)):
    Accession = accessions[pid]
    PatientID = patients[pid]
    subprocess.call("./movescu -c AE_ARCH2@163.246.177.5:104 -b BMIPACS2:4243 -M PatientRoot -m PatientID={0} -m AccessionNumber={1} --dest BMIPACS2".format(PatientID, Accession), shell=True)
      
 
# Record the total run-time
logging.info('Total run time: %s %s', time.time() - t_start, ' seconds!')

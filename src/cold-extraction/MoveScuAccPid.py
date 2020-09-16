import logging
import os
import csv
import time
import shutil
import subprocess

LOGGER = logging.getLogger('pynetdicom')
LOGGER.setLevel(logging.INFO)

# Correctly include the location of the DCM4CHE_BIN. Needs to be set only once. Not for subsequent executions as this value does not change.
DCM4CHE_BIN = "/opt/localdrive/dcm4che-5.19.0/bin"

# Enter the correct csv file name. Assumed to be in the current folder as this file. Otherwise, provide full path or relative path.
# patient_index, the column location of EMPI in the CSV. Entry count starts with 0.
# accession_index, the column location of Accession in the CSV.
csvfile = "ILD_data.csv"
patient_index = 4
accession_index = 5

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
    # Set the values accordingly.
    subprocess.call("./movescu -c AE_ARCH2@163.246.177.5:104 -b BMIPACS2:4243 -M PatientRoot -m PatientID={0} -m AccessionNumber={1} --dest BMIPACS2".format(PatientID, Accession), shell=True)
      
 
# Record the total run-time
logging.info('Total run time: %s %s', time.time() - t_start, ' seconds!')

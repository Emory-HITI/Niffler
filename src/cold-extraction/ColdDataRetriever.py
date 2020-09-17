import logging
import os
import csv
import time
import shutil
import subprocess
import datetime


logging.basicConfig(filename='niffler.log',level=logging.INFO)

DCM4CHE_BIN = "/opt/localdrive/dcm4che-5.19.0/bin"

# Enter the correct csv file name with a relative path to the current folder or a full path. By default, assumed to be in a "csv" folder in the current folder.
csvfile = "csv/empi_accession.csv"

# Correct types: empi_accession, accession, empi_date.
extraction_type = "empi_accession"

# For extraction_type = "accession".
# i.e., for extractions with Accessions only (no EMPI provided).
# accession_index, the column location of Accession in the CSV. Entry count starts with 0.
accession_index = 1
accessions = []


# For extraction_type = "empi_accession" or "empi_date".
# i.e., for extractions with (EMPI and an accession) or (EMPI and a date).
# patient_index, the column location of EMPI in the CSV. Entry count starts with 0.
patient_index = 0
patients = []


# For extraction_type = "empi_date".
# i.e., for extractions with EMPI and a date.
# dateType can range from AcquisitionDate, StudyDate, etc. Replace Accordingly.
# Make sure to replace the date_format to fit the format provided in the csv file. Given below is the default format provided in several PACS.
date_index = 1
dateType = "StudyDate"
date_format = '%m%d%y' #or %m/%d/%y, %m-%d-%y, %Y%m%d, etc
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
        # Set the values accordingly. Needs to be set only once. Not for subsequent executions as this value does not change.
        # BMIPACS2:4243 here refers to the destination AETitle and port. 
        # Replace it with the appropriate AE_Title and port. That must be same AE_Title and port as the one you gave for the storescp process.
        # AE_ARCH2@163.246.177.5:104 is the source AE_Title, followed by the source ip and port. Replace them accordingly.
        subprocess.call("{0}/movescu -c AE_ARCH2@163.246.177.5:104 -b BMIPACS2:4243 -M PatientRoot -m PatientID={1} -m AccessionNumber={2} --dest BMIPACS2".format(DCM4CHE_BIN, PatientID, Accession), shell=True)

# For the cases that does not have the typical EMPI and Accession values together.
elif (extraction_type == 'empi_date' or extraction_type == 'accession'):
 
    # Create our Identifier (query) dataset
    for pid in range(0, length):
        if (extraction_type == 'empi_date'):
            Date = dates[pid]
            PatientID = patients[pid]
            # Set the values accordingly. Needs to be set only once. Not for subsequent executions as this value does not change.
            # BMIPACS2:4243 here refers to the destination AETitle and port. 
            # Replace it with the appropriate AE_Title and port. That must be same AE_Title and port as the one you gave for the storescp process.
            # AE_ARCH2@163.246.177.5:104 is the source AE_Title, followed by the source ip and port. Replace them accordingly.
            subprocess.call("{0}/findscu -c AE_ARCH2@163.246.177.5:104 -b BMIPACS2:4243 -m PatientID={1} -m {2}={3}  -r StudyInstanceUID -x stid.csv.xsl --out-cat --out-file intermediate.csv --out-dir .".format(DCM4CHE_BIN, PatientID, dateType, Date), shell=True)
        elif (extraction_type == 'accession'):
            Accession = accessions[pid]
            # Set the values accordingly. Needs to be set only once. Not for subsequent executions as this value does not change.
            # BMIPACS2:4243 here refers to the destination AETitle and port. 
            # Replace it with the appropriate AE_Title and port. That must be same AE_Title and port as the one you gave for the storescp process.
            # AE_ARCH2@163.246.177.5:104 is the source AE_Title, followed by the source ip and port. Replace them accordingly.
            subprocess.call("{0}/findscu -c AE_ARCH2@163.246.177.5:104 -b BMIPACS2:4243 -m AccessionNumber={1} -r PatientID  -r StudyInstanceUID -x stid.csv.xsl --out-cat --out-file intermediate.csv --out-dir .".format(DCM4CHE_BIN, Accession), shell=True)

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
            # Set the values accordingly. Needs to be set only once. Not for subsequent executions as this value does not change.
            # BMIPACS2:4243 here refers to the destination AETitle and port. 
            # Replace it with the appropriate AE_Title and port. That must be same AE_Title and port as the one you gave for the storescp process.
            # AE_ARCH2@163.246.177.5:104 is the source AE_Title, followed by the source ip and port. Replace them accordingly.
            subprocess.call("{0}/movescu -c AE_ARCH2@163.246.177.5:104 -b BMIPACS2:4243 -M PatientRoot -m PatientID={1} -m StudyInstanceUID={2} --dest BMIPACS2".format(DCM4CHE_BIN,Patient, Study), shell=True)
 
# Record the total run-time
logging.info('Total run time: %s %s', time.time() - t_start, ' seconds!')

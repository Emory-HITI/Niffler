from pydicom.dataset import Dataset

from pynetdicom import (AE, StoragePresentationContexts, evt,
    PYNETDICOM_IMPLEMENTATION_UID,
    PYNETDICOM_IMPLEMENTATION_VERSION)
from pynetdicom.sop_class import (
    PatientRootQueryRetrieveInformationModelFind,
    PatientRootQueryRetrieveInformationModelMove
)
import logging
import os
import csv
import time

# Global Constants: Configurations and folder locations
PATIENTID_KNOWN = True

LOGGER = logging.getLogger('pynetdicom')
LOGGER.setLevel(logging.INFO)


# Constants
root = "/labs/banerjeelab/researchpacs_data/covid19"
csvfile = "All_Covid_Pos_EMPI.csv"
accession_index = 0
# Array of accession numbers
accessions = []

# record the start time
t_start = time.time()

with open(csvfile, newline='') as f:
    reader = csv.reader(f)
    next(f)
    for row in reader:
        accessions.append(row[accession_index])

if not os.path.exists(root):
    os.mkdir(root)

os.chdir(root)


# Implement a handler evt.EVT_C_STORE
def handle_store(event):
 
    """Handle a C-STORE request event."""
    # Decode the C-STORE request's *Data Set* parameter to a pydicom Dataset
    ds = event.dataset

    # Add the File Meta Information
    ds.file_meta = event.file_meta

    ds.is_little_endian = True
    ds.is_implicit_VR = False
    
    os.chdir(root)

    if not os.path.exists(ds.PatientID):
        os.mkdir(ds.PatientID)
    os.chdir(ds.PatientID)
    if not os.path.exists(ds.StudyInstanceUID):
        os.mkdir(ds.StudyInstanceUID)
    os.chdir(ds.StudyInstanceUID)
    # Save the dataset using the SOP Instance UID as the filename
    ds.save_as(ds.SOPInstanceUID + ".dcm", write_like_original=False)
    
    os.chdir(root)
    
    # Return a 'Success' status
    return 0x0000

handlers = [(evt.EVT_C_STORE, handle_store)]




# Initialise the Application Entity for C-FIND
ae = AE()
# Start the storage SCP on port 4243

ae.ae_title = b'BMIPACS2'
ae.port = 4243

# Add a requested presentation context
ae.add_requested_context(PatientRootQueryRetrieveInformationModelFind)



# Initialise the Application Entity for C-MOV
ae2 = AE()

# Add the storage SCP's supported presentation contexts
ae2.supported_contexts = StoragePresentationContexts

# Start the storage SCP on port 4243

ae2.ae_title = b'BMIPACS2'
ae2.port = 4243
scp = ae2.start_server(('', 4243), block=False, evt_handlers=handlers) # Researchpacs

# Add a requested presentation context
ae2.add_requested_context(PatientRootQueryRetrieveInformationModelMove)



# Create our Identifier (query) dataset
for acc_id in range(0, len(accessions)):
    ds = Dataset()
    ds.QueryRetrieveLevel = 'PATIENT'
    
    if PATIENTID_KNOWN:
        ds.PatientID = accessions[acc_id]      
    else:
        ds.AccessionNumber = accessions[acc_id]
        ds.PatientID = ''


        assoc = ae.associate('163.246.177.5', 104, ae_title=b'AE_ARCH2')     # From radiology at AE_ARCH2
        if assoc.is_established:
            # Use the C-FIND service to send the identifier
            # A query_model value of 'P' means use the 'Patient Root Query Retrieve
            #     Information Model - Find' presentation context
            responses = assoc.send_c_find(ds, query_model='P')
    
            for (status, identifier) in responses:
                if status:
                    logging.info('C-FIND query status: 0x{0:04x}'.format(status.Status))
                    # If the status is 'Pending' then `identifier` is the C-FIND response
                    if status.Status in (0xFF00, 0xFF01):
                        ds.PatientID = identifier.PatientID
                else:
                    logging.error('Connection timed out, was aborted or received invalid response')
            # Release the association
            assoc.release()
        else:
            logging.error('Association rejected, aborted or never connected')



    assoc2 = ae2.associate('163.246.177.5', 104, ae_title=b'AE_ARCH2')   # From radiology
    if assoc2.is_established:
        logging.debug('Association Established')
        # Use the C-MOVE service to send the identifier
        # A query_model value of 'P' means use the 'Patient Root Query
        #   Retrieve Information Model - Move' presentation context
        responses = assoc2.send_c_move(ds, b'BMIPACS2', query_model='P')
    
        for (status, identifier) in responses:
            if status:
                logging.info('C-MOVE query status: 0x{0:04x}'.format(status.Status))
                if status.Status in (0xFF00, 0xFF01):
                    logging.info(identifier)
            else:
                logging.error('Connection timed out, was aborted or received invalid response')        


        # Release the association
        assoc2.release()
        logging.debug('Association Released')
    else:
        logging.debug('Association rejected or aborted')


# Record the total run-time
logging.info('Total run time: %s %s', time.time() - t_start, ' seconds!')

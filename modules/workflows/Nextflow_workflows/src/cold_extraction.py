import os
import sys
import argparse
import logging
import time
import shutil
import schedule
import signal

script_dir = os.path.dirname( __file__ )
module_dir=os.path.join(script_dir,"..","..","..","cold-extraction")
print("script_dir is:",module_dir)
sys.path.append( module_dir )
import ColdDataRetriever


ap = argparse.ArgumentParser()
ap.add_argument("--NifflerSystem")
ap.add_argument("--StorageFolder")
ap.add_argument("--FilePath")
ap.add_argument("--CsvFile")
ap.add_argument("--NumberOfQueryAttributes",  type=int)
ap.add_argument("--FirstAttr")
ap.add_argument("--FirstIndex", type=int)
ap.add_argument("--SecondAttr")
ap.add_argument("--SecondIndex",  type=int)
ap.add_argument("--ThirdAttr")
ap.add_argument("--ThirdIndex", type=int)
ap.add_argument("--DateFormat")
ap.add_argument("--SendEmail",  type=bool)
ap.add_argument("--YourEmail")
ap.add_argument("--DCM4CHEBin")
ap.add_argument("--SrcAet")
ap.add_argument("--QueryAet")
ap.add_argument("--DestAet")
ap.add_argument("--NightlyOnly", type=bool)
ap.add_argument("--StartHour", type=int)
ap.add_argument("--EndHour", type=int)
ap.add_argument("--NifflerID", type=int)
ap.add_argument("--MaxNifflerProcesses", type=int)
valuesDict = vars(ap.parse_args())

ColdDataRetriever.storage_folder = valuesDict['StorageFolder']
ColdDataRetriever.file_path = valuesDict['FilePath']
ColdDataRetriever.csv_file = valuesDict['CsvFile']
ColdDataRetriever.number_of_query_attributes = int(valuesDict['NumberOfQueryAttributes'])
ColdDataRetriever.first_index = int(valuesDict['FirstIndex'])
ColdDataRetriever.second_index = int(valuesDict['SecondIndex'])
ColdDataRetriever.third_index = int(valuesDict['ThirdIndex'])
ColdDataRetriever.first_attr = valuesDict['FirstAttr']
ColdDataRetriever.second_attr = valuesDict['SecondAttr']
ColdDataRetriever.third_attr = valuesDict['ThirdAttr']
ColdDataRetriever.date_format = valuesDict['DateFormat']
ColdDataRetriever.email = valuesDict['YourEmail']
ColdDataRetriever.send_email = bool(valuesDict['SendEmail'])
ColdDataRetriever.mod_csv_file = ColdDataRetriever.csv_file[:-4]+'_mod.csv'
shutil.copyfile(ColdDataRetriever.csv_file, ColdDataRetriever.mod_csv_file)

ColdDataRetriever.DCM4CHE_BIN = valuesDict['DCM4CHEBin']
ColdDataRetriever.SRC_AET = valuesDict['SrcAet']
ColdDataRetriever.QUERY_AET = valuesDict['QueryAet']
ColdDataRetriever.DEST_AET = valuesDict['DestAet']
ColdDataRetriever.NIGHTLY_ONLY = False
ColdDataRetriever.START_HOUR = int(valuesDict['StartHour'])
ColdDataRetriever.END_HOUR = int(valuesDict['EndHour'])
ColdDataRetriever.IS_EXTRACTION_NOT_RUNNING = True
ColdDataRetriever.NIFFLER_ID = int(valuesDict['NifflerID'])
ColdDataRetriever.MAX_PROCESSES = int(valuesDict['MaxNifflerProcesses'])
ColdDataRetriever.SEPARATOR = ','

ColdDataRetriever.firsts = []
ColdDataRetriever.seconds = []
ColdDataRetriever.thirds = []

ColdDataRetriever.storescp_processes = 0
ColdDataRetriever.niffler_processes = 0

ColdDataRetriever.nifflerscp_str = "storescp.*{0}".format(ColdDataRetriever.QUERY_AET)
ColdDataRetriever.niffler_str = 'ColdDataRetriever'

ColdDataRetriever.cfind_only = 'CFIND-ONLY'
ColdDataRetriever.cfind_detailed = 'CFIND-DETAILED'

ColdDataRetriever.temp_folder = os.path.join(ColdDataRetriever.storage_folder, "cfind-temp")

if ColdDataRetriever.file_path == ColdDataRetriever.cfind_only:
    ColdDataRetriever.cfind_add = '-r StudyDescription -x description.csv.xsl'
    ColdDataRetriever.out_folder = ColdDataRetriever.temp_folder
elif ColdDataRetriever.file_path == ColdDataRetriever.cfind_detailed:
    ColdDataRetriever.cfind_add = '-r StudyDescription -r StudyDate -r StudyTime -r DeviceSerialNumber -r ProtocolName ' \
                '-r PerformedProcedureStepDescription -r NumberOfStudyRelatedSeries -r  ' \
                'NumberOfStudyRelatedInstances -r AcquisitionDate ' \
                '-x detailed.csv.xsl'
    ColdDataRetriever.out_folder = temp_folder
else:
    ColdDataRetriever.cfind_add = ' -x stid.csv.xsl '
    ColdDataRetriever.out_folder = '.'

ColdDataRetriever.niffler_log = 'niffler' + str(ColdDataRetriever.NIFFLER_ID) + '.log'

logging.basicConfig(filename=ColdDataRetriever.niffler_log, level=logging.INFO)
logging.getLogger('schedule').setLevel(logging.WARNING)

# Variables to track progress between iterations.
global extracted_ones
ColdDataRetriever.extracted_ones = list()

# By default, assume that this is a fresh extraction.
ColdDataRetriever.resume = False

# All extracted files from the csv file are saved in a respective .pickle file.
try:
    with open(ColdDataRetriever.csv_file + '.pickle', 'rb') as f:
        ColdDataRetriever.extracted_ones = pickle.load(f)
        # Since we have successfully located a pickle file, it indicates that this is a resume.
        ColdDataRetriever.resume = True
except:
    logging.info("No existing pickle file found. Therefore, initialized with empty value to track the progress to "
                 "{0}.pickle.".format(ColdDataRetriever.csv_file))

# record the start time
ColdDataRetriever.t_start = time.time()

ColdDataRetriever.read_csv()
    # The thread scheduling
schedule.every(1).minutes.do(ColdDataRetriever.run_threaded, ColdDataRetriever.run_retrieval)    
schedule.every(10).minutes.do(ColdDataRetriever.run_threaded, ColdDataRetriever.update_pickle)

# Keep running in a loop.
while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except KeyboardInterrupt:
        ColdDataRetriever.check_kill_process()
        logging.shutdown()
        break
        

for line in os.popen("ps -ax | grep storescp"):
        fields = line.split()
        pid = fields[0]
        print(pid)
        os.kill(int(pid), signal.SIGKILL)


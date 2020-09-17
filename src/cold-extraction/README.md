# The On-Demand Retrospective DICOM Extractor
This extractor retrieves DICOM images on-demand, based on a CSV file provided by the user. Below we discuss the steps to run Niffler on-demand DICOM extraction queries.


# CSV file with correct format.

First, place the csv file adhering to the correct formats in a folder.

Please include a header for the csv, such as "EMPI,Accession", as otherwise the first line will be ignored.

The format examples:
[1]
EMPI,Accession

AAAAA,BBBBBYYBBBBB

AAAAA,BBBBBYYBBBBB

AAAAA,BBBBBYYBBBBB

[2]
EMPI, Study Date

AAAAA, 20180723

AAAAA, 20180724

AAAAA, 20180725

Make sure the accession's year is in the YY format.


[3]
Accession

BBBBBYYBBBBB

BBBBBYYBBBBB

BBBBBYYBBBBB


# Running StoreSCP

We first run a StoreScp process.

Start a new StoreSCP pointing to an empty directory in a folder that has write access to the script as a nohup.

Let's use /opt/data

$ ps -xa | grep storescp

149238 pts/0    S+     0:00 grep storescp

If only the above line is present, that means no other storescp process is running. You can start a new storescp process in that case.

$ cd /opt/data

Create a new folder with a decent name that can be easy to match back with your study with a descriptive name. Here we create the folder, 

$ mkdir A-NEW-FOLDER


$ nohup DCM4CHE-HOME/bin/storescp --accept-unknown --directory DICOM-STORAGE-FULLPATH --filepath {00100020}/{0020000D}/{0020000E}/{00080018}.dcm -b DEST_AET:DEST_PORT > storescp.out &

* Replace DCM4CHE-HOME with the absolute location where DCM4CHE is extracted (i.e., installed).

* Replace DICOM-STORAGE-FULLPATH with the absolute location of the directory where you want your Dicom files to be stored. This folder will be used as the root, and the dicom images will be stored in patient/study/series/instance.dcm hierarchy.

For example,

$ nohup /opt/dcm4che-5.19.0/bin/storescp --accept-unknown --directory /opt/data/A-NEW-FOLDER --filepath {00100020}/{0020000D}/{0020000E}/{00080018}.dcm -b QBNIFFLER:4243 > storescp.out &




# Running the Niffler Retrospective Data Retriever

Make sure to follow the comments in the ColdDataRetriever.py to adopt the values accordingly.

Then run the ColdDataRetriever.py, which consists of a MoveScu process that often following a FindScu. 

$ cd /opt/Niffler/src/cold-extraction

$ nohup python3.6 ColdDataRetriever.py > cold.out &


# Check the Progress

After some time (may take a few hours to a few days, depending on the length of the CSV file), check whether the extraction is complete.

$ ps -xa | grep python

If the ColdDataRetriever.py that you started is still running, wait for them to complete and check again later.


# Completion

Once they are complete, make sure to kill your storescp process. This will make sure that the next person does not mistakenly send their data to your storescp process.

$ ps -xa | grep storescp

148923 pts/0    Sl     0:01 java -cp /opt/dcm4che-5.19.0/etc/storescp/:/opt/dcm4che-5.19.0/etc/certs/:/opt/dcm4che-5.19.0/lib/dcm4che-tool-storescp-5.19.0.jar:/opt/dcm4che-5.19.0/lib/dcm4che-core-5.19.0.jar:/opt/dcm4che-5.19.0/lib/dcm4che-net-5.19.0.jar:/opt/dcm4che-5.19.0/lib/dcm4che-tool-common-5.19.0.jar:/opt/dcm4che-5.19.0/lib/slf4j-api-1.7.25.jar:/opt/dcm4che-5.19.0/lib/slf4j-log4j12-1.7.25.jar:/opt/dcm4che-5.19.0/lib/log4j-1.2.17.jar:/opt/dcm4che-5.19.0/lib/commons-cli-1.4.jar org.dcm4che3.tool.storescp.StoreSCP --accept-unknown --directory /opt/data/test --filepath {00100020}/{0020000D}/{0020000E}/{00080018}.dcm -b QBNIFFLER:4243

 149221 pts/0    S+     0:00 grep storescp


$ kill pid/THE-PROCESS-ID

In this case,

$ kill 148923

Check again that the Storescp is killed.

$ ps -xa | grep storescp

 149238 pts/0    S+     0:00 grep storescp

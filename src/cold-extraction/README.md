# The On-Demand Retrospective DICOM Extractor
Cold Data Retriever is another script that pulls and extracts data on-demand. It is initiated per user query, rather than running continuously.

## Running StoreSCP
We first run a StoreScp process.

$ nohup DCM4CHE-HOME/bin/storescp --accept-unknown --directory DICOM-STORAGE-FULLPATH --filepath {00100020}/{0020000D}/{0020000E}/{00080018}.dcm -b BMIPACS2:4243 > storescp.out &

* Replace DCM4CHE-HOME with the absolute location where DCM4CHE is extracted (i.e., installed).

* Replace DICOM-STORAGE-FULLPATH with the absolute location of the directory where you want your Dicom files to be stored. This folder will be used as the root, and the dicom images will be stored in patient/study/series/instance.dcm hierarchy.

For example,

$ nohup /opt/localdrive/dcm4che-5.19.0/bin/storescp --accept-unknown --directory /labs/banerjeelab/DBS_EMPI --filepath {00100020}/{0020000D}/{0020000E}/{00080018}.dcm -b BMIPACS2:4243 > storescp.out &

## Running the Retrospective (Cold) Data Retriever

Then run the ColdDataRetriever.py, which consists of a MoveScu process that often following a FindScu. 

$ nohup python3.6 ColdDataRetriever.py > cold.out &

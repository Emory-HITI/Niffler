# The On-Demand Retrospective DICOM Extractor
Cold Data Retriever is another script that pulls and extracts data on-demand. It is initiated per user query, rather than running continuously.

## Running StoreSCP
We first run a StoreScp process.

$ cd /opt/localdrive/dcm4che-5.19.0/bin

$ nohup ./storescp --accept-unknown --directory /labs/banerjeelab/qbniffler --filepath {00100020}/{0020000D}/{0020000E}/{00080018}.dcm -b BMIPACS2:4243 > storescp.out &

## Running the Retrospective (Cold) Data Retriever

Then run the ColdDataRetriever.py, which consists of a MoveScu process that often following a FindScu. 

$ nohup python3.6 ColdDataRetriever.py > cold.out &

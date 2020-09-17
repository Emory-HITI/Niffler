# The Niffler On-Demand Retrospective DICOM Extractor
This extractor retrieves DICOM images on-demand, based on a CSV file provided by the user. Below we discuss the steps to run Niffler on-demand DICOM extraction queries.


# Configuring Niffler On-Demand Extractor

Unless you are the administrator who is configuring Niffler for the first time, skip and proceed to the section "Using Niffler".

system.json entries are to be set *only once* for the Niffler deployment by the administrator. Once set, further extractions do not require a change.

* *DCM4CHEBin*: Set the correct location of the DCM4_CHE folder.

* *SrcAet*: Set the correct AET@HOST:PORT of the source.

* *QueryAet*: Set the correct AET:PORT of the querying AET (i.e., this script). Typically same as the values you set for the storescp.

* *DestAet*:   Set the correct AET of the detination AET. Must match the AET of the storescp.



# Using Niffler

## CSV file with correct format.

First, place the csv file adhering to the correct formats in a folder (by default, a folder named "csv" in the current folder).


* Please retrieve the CSV (not xlsx) file consisting of the images that must be acquired via Niffler.

* Each C-MOVE extraction should be represented by a separate line.

* Please make sure to use EMPI and not MRN or Institution-specific patient identifiers.

* Please include a header for the csv, such as "EMPI,Accession", as otherwise the first line will be ignored.

* Usual fields that Niffler supports by default: AccessionNumber, AccessionNumber and EMPI, EMPI and a date (indicate whether StudyDate or AcquisitionDate). 

The format examples:

[1]

EMPI,Accession

AAAAA,BBBBBYYBBBBB

AAAAA,BBBBBYYBBBBB

AAAAA,BBBBBYYBBBBB

[2]

EMPI, Study Date

AAAAA,20180723

AAAAA,20180724

AAAAA,20180725

Make sure the accession's year is in the YY format.


[3]
Accession

BBBBBYYBBBBB

BBBBBYYBBBBB

BBBBBYYBBBBB


## Running StoreSCP

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


## Configuring Extraction Profile with config.json.

config.json entries are to be set *for each* Niffler on-demand DICOM extractions.

* *CsvFile*: Enter the correct csv file name with a relative path to the current folder or a full path. The default value given assumes the CSV file to be in a "csv" folder in the current folder.

* *ExtractionType*: Currently supported options, empi_accession (extractions based on EMPI and AccessionNumber), accession (extractions based solely on AccessionNumber), empi_date (extractions based on EMPI and a date such as StudyDate or AcquisitionDate).

* *AccessionIndex*: Set the CSV column index of AccessionNumber for extractions with Accessions (with or without EMPI provided). Entry count starts with 0. For extractions other than types of accession and empi_accession, leave this entry unmodified.

* *PatientIndex*: Set the CSV column index of EMPI for extractions with (EMPI and an accession) or (EMPI and a date). For extractions without EMPI, leave this entry unmodified.

* *DateIndex*: Set the CSV column index of Date (StudyDate, AcquisitionDate, ..) for extractions with EMPI and a date. For extractions without a Date, leave this entry unmodified.

* *DateType*: DateType can range from AcquisitionDate, StudyDate, etc. Replace Accordingly. For extractions without a Date, leave this entry unmodified.

* *DateFormat*: DateFormat can range from %Y%m%d, %m/%d/%y, %m-%d-%y, %%m%d%y, etc. For extractions without a Date, leave this entry unmodified.


## Running the Niffler Retrospective Data Retriever

Then run the ColdDataRetriever.py, which consists of a MoveScu process that often following a FindScu. 

$ cd /opt/Niffler/src/cold-extraction

$ nohup python3.6 ColdDataRetriever.py > cold.out &


## Check the Progress

After some time (may take a few hours to a few days, depending on the length of the CSV file), check whether the extraction is complete.

$ ps -xa | grep python

If the ColdDataRetriever.py that you started is still running, wait for them to complete and check again later.


## Completion

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

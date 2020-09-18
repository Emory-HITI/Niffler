# The Niffler On-Demand Retrospective DICOM Extractor
This extractor retrieves DICOM images on-demand, based on a CSV file provided by the user. Below we discuss the steps to run Niffler on-demand DICOM extraction queries.


# Configuring Niffler On-Demand Extractor

Unless you are the administrator who is configuring Niffler for the first time, skip this section and proceed to the section "Using Niffler".

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


## Configuring Extraction Profile with config.json.

config.json entries are to be set *for each* Niffler on-demand DICOM extractions.

* *StorageFolder*: Create a folder where you like your DICOM files to be. Usually, this is an empty folder (since each extraction is unique). Make sure the python program has write access to that folder.

* *FilePath*: By default, "{00100020}/{0020000D}/{0020000E}/{00080018}.dcm". This indicates a hierarchical storage of patients/studies/series/instances.dcm. Leave this value as it is unless you want to change the hierarchy.

* *CsvFile*: Enter the correct csv file name with a relative path to the current folder or a full path. The default value given assumes the CSV file to be in a "csv" folder in the current folder.

* *ExtractionType*: Currently supported options, empi_accession (extractions based on EMPI and AccessionNumber), accession (extractions based solely on AccessionNumber), empi_date (extractions based on EMPI and a date such as StudyDate or AcquisitionDate).

* *AccessionIndex*: Set the CSV column index of AccessionNumber for extractions with Accessions (with or without EMPI provided). Entry count starts with 0. For extractions other than types of accession and empi_accession, leave this entry unmodified.

* *PatientIndex*: Set the CSV column index of EMPI for extractions with (EMPI and an accession) or (EMPI and a date). For extractions without EMPI, leave this entry unmodified.

* *DateIndex*: Set the CSV column index of Date (StudyDate, AcquisitionDate, ..) for extractions with EMPI and a date. For extractions without a Date, leave this entry unmodified.

* *DateType*: DateType can range from AcquisitionDate, StudyDate, etc. Replace Accordingly. For extractions without a Date, leave this entry unmodified.

* *DateFormat*: DateFormat can range from %Y%m%d, %m/%d/%y, %m-%d-%y, %%m%d%y, etc. For extractions without a Date, leave this entry unmodified.


## Running the Niffler Retrospective Data Retriever

First make sure there is no other Niffler ColdDataRetriever.py python process is running.

$ ps -xa | grep python3

 163287 pts/0    S      0:00 python3 ColdDataRetriever.py

If a ColdDataRetriever.py that was previously started is still running, wait for it to complete and check again later. Do *NOT* start another ColdDataRetriever.py when the previous one is still running. That will mix the files from both extractions to a single folder (as currently only single DICOM connection can exist in our set up).

Once there is no other process, then you can run your own extraction process. 

$ cd /opt/Niffler/src/cold-extraction

$ nohup python3 ColdDataRetriever.py > cold.out &


## Check the Progress

After some time (may take a few hours to a few days, depending on the length of the CSV file), check whether the extraction is complete.

$ ps -xa | grep python3

If the ColdDataRetriever.py that you started is still running, check again a few hours or days later depending on how large your CSV file was!

Once completed, all the relevant DICOM files will be in the *StorageFolder* folder.
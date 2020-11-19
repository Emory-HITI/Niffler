# The Niffler On-Demand Retrospective DICOM Extractor
This extractor retrieves DICOM images on-demand, based on a CSV file provided by the user. Below we discuss the steps to run Niffler on-demand DICOM extraction queries. 

First go to the src/cold-extraction directory in the Niffler source code in your server.

For example, assuming Niffler is checked out in the /opt folder,

$ cd /opt/Niffler/src/cold-extraction

Then proceed to the below steps.



# Configuring Niffler On-Demand Extractor

Unless you are the administrator who is configuring Niffler for the first time, skip this section and proceed to the section "Using Niffler".

Find the system.json file in the folder and modify accordingly.

system.json entries are to be set *only once* for the Niffler deployment by the administrator. Once set, further extractions do not require a change.

* *DCM4CHEBin*: Set the correct location of the DCM4_CHE folder.

* *SrcAet*: Set the correct AET@HOST:PORT of the source.

* *QueryAet*: Set the correct AET:PORT of the querying AET (i.e., this script). Typically same as the values you set for the storescp.

* *DestAet*:   Set the correct AET of the detination AET. Must match the AET of the storescp.

* *NightlyOnly*: This is set to "True" by default. Setting it to anything else will make Niffler on-demand extraction run at any time.
	
* *StartHour*: When a night-only mode is enabled, when should the extraction start. A rough 24 hour time (hours only), calculated by the hour. Not an exact time.

* *EndHour*: When should the extraction end, when the night-mode is enabled. By default, the start hour is 21 and end hour is 9.


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

Find the config.json file in the folder and modify accordingly.

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


$ nohup python3 ColdDataRetriever.py > UNIQUE-OUTPUT-FILE-FOR-YOUR-EXTRACTION.out &

Check that the extraction is going smooth, by,

$ tail -f UNIQUE-OUTPUT-FILE-FOR-YOUR-EXTRACTION.out

You will see lots of logs.

Now, if you see no log lines, most likely case is, a failure due to an on-going previous extraction. Check the Niffler logs.

$ tail -f niffler.log

INFO:root:Number of running niffler processes: 2 and storescp processes: 1

ERROR:root:[EXTRACTION FAILURE] 2020-09-21 17:42:24.760598: Previous extraction still running. As such, your extraction attempt was not suuccessful this time. Please wait until that completes and re-run your query.

Try again later. Once there is no other process, then you can run your own extraction process. 



## Check the Progress

After some time (may take a few hours to a few days, depending on the length of the CSV file), check whether the extraction is complete.

$ tail -f niffler.log

INFO:root:[EXTRACTION COMPLETE] 2020-09-21 17:42:38.465501: Niffler Extraction to /opt/data/new-study Completes. Terminating the completed storescp process.



## Troubleshooting

If the process fails even when no one else's Niffler process is running, check your log file (UNIQUE-OUTPUT-FILE-FOR-YOUR-EXTRACTION.out)

If you find an error such as: "IndexError: list index out of range", that indicates your csv file and/or config.json are not correctly set.

Fix them and restart your Python process, by first finding and killing your python process and then starting Niffler as before.

$ ps -xa | grep python

1866 ?    Ss   0:00 /usr/bin/python3 /usr/bin/networkd-dispatcher --run-startup-triggers

  1936 ?    Ssl  0:00 /usr/bin/python3 /usr/share/unattended-upgrades/unattended-upgrade-shutdown --wait-for-signal

  2926 pts/0  T   0:00 python3 ColdDataRetriever.py

  3384 pts/0  S+   0:00 grep --color=auto python

$ kill -9 2926

You might need to run the above command with sudo to find others' Niffler processes.

Make sure not to kill others' Niffler processes. So double-check and confirm that the running process is indeed the one that was started by you, and yet failed.


Rarely, a storescp process started by another user becomes a zombie and prevents Niffler from starting. If that happens, check for storescp processes and kill them as well. Please make sure you are killing only the on-demand Niffler storescp process. By default, this will be shown QBNIFFLER:4243 as below.

$ sudo ps -xa | grep storescp

241720 pts/4  Sl   0:02 java -cp /opt/dcm4che-5.22.5/etc/storescp/:/opt/dcm4che-5.22.5/etc/certs/:/opt/dcm4che-5.22.5/lib/dcm4che-tool-storescp-5.22.5.jar:/opt/dcm4che-5.22.5/lib/dcm4che-core-5.22.5.jar:/opt/dcm4che-5.22.5/lib/dcm4che-net-5.22.5.jar:/opt/dcm4che-5.22.5/lib/dcm4che-tool-common-5.22.5.jar:/opt/dcm4che-5.22.5/lib/slf4j-api-1.7.30.jar:/opt/dcm4che-5.22.5/lib/slf4j-log4j12-1.7.30.jar:/opt/dcm4che-5.22.5/lib/log4j-1.2.17.jar:/opt/dcm4che-5.22.5/lib/commons-cli-1.4.jar org.dcm4che3.tool.storescp.StoreSCP --accept-unknown --directory /home/Data/Mammo/Kheiron/cohort_1/ --filepath {00100020}/{0020000D}/{0020000E}/{00080018}.dcm -b QBNIFFLER:4243 242185 pts/5  S+   0:00 grep --color=auto storescp

$ sudo kill -9 241720

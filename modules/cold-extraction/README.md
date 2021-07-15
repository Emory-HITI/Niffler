# The Niffler On-Demand Retrospective DICOM Extractor

The retrospective DICOM Extractor retrieves DICOM images on-demand, based on a CSV file provided by the user. Below we discuss the steps to run Niffler on-demand DICOM extraction queries. 


# Configuring Niffler On-Demand Extractor

Unless you are the administrator who is configuring Niffler for the first time, skip this section and proceed to the section "Using Niffler".

Find the system.json file in the folder and modify accordingly.

system.json entries are to be set *only once* for the Niffler deployment by the administrator. Once set, further extractions do not require a change.

* *DCM4CHEBin*: Set the correct location of the DCM4_CHE folder.

* *SrcAet*: Set the correct AET@HOST:PORT of the source.

* *QueryAet*: Set the correct AET:PORT of the querying AET (i.e., this script). Typically same as the values you set for the storescp.

* *DestAet*:   Set the correct AET of the detination AET. Must match the AET of the storescp.

* *NightlyOnly*: This is set to _true_ by default. Setting it to _false_ will make Niffler on-demand extraction run at any time.
	
* *StartHour*: When a night-only mode is enabled, when should the extraction start. A rough 24 hour time (hours only), calculated by the hour. Not an exact time.

* *EndHour*: When should the extraction end, when the night-mode is enabled. By default, the start hour is 19 and end hour is 7.

* *NifflerID*: The ID of the current execution. Default is 1. You must increment the second execution to 2, so that the logs are properly stored in niffler1.log and niffler2.log.

* *MaxNifflerProcesses*: How many Niffler processes can run in parallel. Make sure each execution has its own SrcAet properly configured. Each SrcAet can run only once.


# Using Niffler

## CSV file with correct format.

First, place the csv file adhering to the correct formats in a folder (by default, a folder named "csv" in the current folder).


* Please retrieve the CSV (not xlsx) file consisting of the images that must be acquired via Niffler.

* Each C-MOVE extraction should be represented by a separate line.

* Please make sure to use EMPI and not MRN or Institution-specific patient identifiers.

* Please include a header for the csv, such as "PatientID,AccessionNumber". The first line is considered the header and will be ignored in the extractions.

* Niffler can support up to 3 C-FIND DICOM keywords in queries. However, please note that the extractions are done internally in either patient level (if the query is just based on PatientID) or study level (for example, a combination of PatientID and AccessionNumber). So, if your matching 3 DICOM keyword extraction is aimed at receiving only particular series, Niffler will in fact retrieve the entire studies of the relevant series. Niffler's granularity for on-demand extraction does not go to series or instances level.

The format examples:
```
[1]
PatientID
AAAAA
AAAAA
AAAAA

[2]
PatientID,AccessionNumber
AAAAA,BBBBBYYBBBBB
AAAAA,BBBBBYYBBBBB
AAAAA,BBBBBYYBBBBB

* Make sure the accession's year is in the YY format.

[3]
PatientID,AccessionNumber,StudyDate
AAAAA,BBBBBYYBBBBB,CCCCCC
AAAAA,BBBBBYYBBBBB,CCCCCC 
AAAAA,BBBBBYYBBBBB,CCCCCC


```

## Configuring Extraction Profile with config.json.

Find the config.json file in the folder and modify accordingly.

config.json entries are to be set *for each* Niffler on-demand DICOM extractions.

All the following config entries can be passed as command line arguments. Prepend "--" to each key and pass as arguments in cli. By default, the values from `config.json` will be used. <br/>
Example: `python3 ./ColdDataRetriever.py --NumberOfQueryAttributes 1 --FirstAttr PatientID --FirstIndex 0`

* *NifflerSystem*: By default, system.json. Provide a custom json file with Niffler system information, if you have any.

* *StorageFolder*: Create a folder where you like your DICOM files to be. Usually, this is an empty folder (since each extraction is unique). Make sure you, i.e., the user that starts Niffler ColdDataRetriever.py, have write access to that folder.

* *FilePath*: By default, "{00100020}/{0020000D}/{0020000E}/{00080018}.dcm". This indicates a hierarchical storage of patients/studies/series/instances.dcm. Leave this value as it is unless you want to change the hierarchy.

* *CsvFile*: Enter the correct csv file name with a relative path to the current folder or a full path. The default value given assumes the CSV file to be in a "csv" folder in the current folder.

* *NumberOfQueryAttributes*: Can be 1, 2, or 3. By default, 1.

**Please note:** It is important to use the correct DICOM keywords such as, "PatientID", "AccessionNumber", "StudyInstanceUID", and "StudyDate".
  Please refer to the DICOM Standard for more information on the DICOM header attributes/keywords.
  Please note, the correct keyword is "AccessionNumber" and not "Accession" or "Accessions". Similarly, it is "PatientID" - neither "EMPI" nor "Patient-ID" (although they all are indeed the same in practice).
  
Please refer to the DICOM standards to ensure you spell the [DICOM keyword](http://dicom.nema.org/dicom/2013/output/chtml/part06/chapter_6.html) correctly, if in doubt.

* *FirstAttr*: Which should be the first attribute. By default, "PatientID".   
  
* *FirstIndex*: Set the CSV column index of first Attribute. By default, 0. Note the index starts at 0.

* *SecondAttr*: Which should be the second attribute. By default, "AccessionNumber". This field is ignored when NumberOfQueryAttributes is 1.

* *SecondIndex*: Set the CSV column index of second Attribute. By default, 1. This field is ignored when NumberOfQueryAttributes is 1.

* *ThirdAttr*: Which should be the third attribute. By default, "StudyDate". This field is ignored when NumberOfQueryAttributes is 1 or 2.

* *ThirdIndex*: Set the CSV column index of third Attribute. By default, 2. This field is ignored when NumberOfQueryAttributes is 1 or 2.

* *DateFormat*: DateFormat can range from %Y%m%d, %m/%d/%y, %m-%d-%y, %%m%d%y, etc. This field is ignored for extractions that do not use a Date as one of their extraction attributes. We have tested with StudyDate. Leave this entry unmodified for such cases. The default is %Y%m%d and works for most cases.

* *SendEmail*: Do you want to send an email notification when the extraction completes? The default is true. You may disable this if you do not want to receive an email upon the completion.

* *YourEmail*: Replace "test@test.test" with a valid email if you would like to receive an email notification. If the SendEmail property is disabled, you can leave this as is.

## Running the Niffler Retrospective Data Retriever

```bash

$ python3 ColdDataRetriever.py

# With Nohup
$ nohup python3 ColdDataRetriever.py > UNIQUE-OUTPUT-FILE-FOR-YOUR-EXTRACTION.out &

# With Command Line Arguments
$ nohup python3 ColdDataRetriever.py --SendEmail false --NumberOfQueryAttributes 1 --FirstAttr AccessionNumber --FirstIndex 0 --CsvFile "csv/accession.csv"> UNIQUE-OUTPUT-FILE-FOR-YOUR-EXTRACTION.out &
```
Check that the extraction is going smooth, by,
```
$ tail -f UNIQUE-OUTPUT-FILE-FOR-YOUR-EXTRACTION.out
```
You will see lots of logs.

Now, if you see no log lines, most likely case is, a failure due to an on-going previous extraction. Check the Niffler logs.
```
$ tail -f niffler1.log
```
Above log might be niffler2.log. The log file is niffler, appended by a number indicated in system.json as NifflerID, where the default value is 1.
```
INFO:root:Number of running niffler processes: 2 and storescp processes: 1

ERROR:root:[EXTRACTION FAILURE] 2020-09-21 17:42:24.760598: Previous extraction still running. As such, your extraction attempt was not suuccessful this time. Please wait until that completes and re-run your query.
```
Try again later. Once there is no other process, then you can run your own extraction process. 



## Check the Progress

After some time (may take a few hours to a few days, depending on the length of the CSV file), check whether the extraction is complete.
```
$ tail -f niffler.log

INFO:root:[EXTRACTION COMPLETE] 2020-09-21 17:42:38.465501: Niffler Extraction to /opt/data/new-study Completes. Terminating the completed storescp process.
```
A pickle file tracks the progress. The pickle file is created by appending ".pickle" to the csv file name.

```
<8c>^X1234, 000056789<94>
```
For "empi_accession" extractions, each entry above is empi,accession. For "empi" extractions, each entry above is empi.

For other combinations of extractions, each entry above will be empi, study. The reason is we have to _translate_ these headers into empi_study for C-MOVE queries.


## Troubleshooting

If the process fails even when no one else's Niffler process is running, check your log file (UNIQUE-OUTPUT-FILE-FOR-YOUR-EXTRACTION.out)

If you find an error such as: "IndexError: list index out of range", that indicates your csv file and/or config.json are not correctly set.

Fix them and restart your Python process, by first finding and killing your python process and then starting Niffler as before.
```
$ ps -xa | grep python

1866 ?    Ss   0:00 /usr/bin/python3 /usr/bin/networkd-dispatcher --run-startup-triggers

1936 ?    Ssl  0:00 /usr/bin/python3 /usr/share/unattended-upgrades/unattended-upgrade-shutdown --wait-for-signal

2926 pts/0  T   0:00 python3 ColdDataRetriever.py

3384 pts/0  S+   0:00 grep --color=auto python

$ kill 2926
```
You might need to run the above command with sudo to find others' Niffler processes.

Make sure not to kill others' Niffler processes. So double-check and confirm that the running process is indeed the one that was started by you, and yet failed.


Rarely, a storescp process started by another user becomes a zombie and prevents Niffler from starting. If that happens, check for storescp processes and kill them as well. Please make sure you are killing only the on-demand Niffler storescp process. By default, this will be shown QBNIFFLER:4243 as below.
```
$ sudo ps -xa | grep storescp

241720 pts/4  Sl   0:02 java -cp /opt/dcm4che-5.22.5/etc/storescp/:/opt/dcm4che-5.22.5/etc/certs/:/opt/dcm4che-5.22.5/lib/dcm4che-tool-storescp-5.22.5.jar:/opt/dcm4che-5.22.5/lib/dcm4che-core-5.22.5.jar:/opt/dcm4che-5.22.5/lib/dcm4che-net-5.22.5.jar:/opt/dcm4che-5.22.5/lib/dcm4che-tool-common-5.22.5.jar:/opt/dcm4che-5.22.5/lib/slf4j-api-1.7.30.jar:/opt/dcm4che-5.22.5/lib/slf4j-log4j12-1.7.30.jar:/opt/dcm4che-5.22.5/lib/log4j-1.2.17.jar:/opt/dcm4che-5.22.5/lib/commons-cli-1.4.jar org.dcm4che3.tool.storescp.StoreSCP --accept-unknown --directory /home/Data/Mammo/Kheiron/cohort_1/ --filepath {00100020}/{0020000D}/{0020000E}/{00080018}.dcm -b QBNIFFLER:4243 242185 pts/5  S+   0:00 grep --color=auto storescp

$ sudo kill 241720
```

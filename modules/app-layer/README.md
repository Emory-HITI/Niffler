# The Niffler Application Layer

The Application Layer consists of the Scanner Utilization computation and scripts such as scanner clock calibration. The application layer can be extended with other functionalities, consuming data from DICOM data, metadata, and processed intermediate files from the data and metadata.


In the folder src/main/resources/

* Replace subset_scanners_sample.csv with the actual scanners, and rename the file to subset_scanners.csv. Only the scanners listed in this csv file will be considered.

* Similarly, replace csv files in the intermediary folder with the actual intermediary csv files, produced by scanner_util.js by tracing the metadata for the previous day. The intermediary file consists of scanner, studyID, patientID, duration, numberOfSeriesInStudy, startTime, endTime values with no header. The scanner utilization is calculated and returned in final_{intermediate}.csv for the day.

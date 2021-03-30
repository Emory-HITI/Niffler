# Niffler Scripts

The scripts, developed in Javascript, includes mechanisms to query the metadata storage to prepare DICOM subsets for the execution of the ML algorithm containers.

* ivcf-query.js: Filters query for the IVC filter detection container

* scanner-time-shift:	Calibrates the time/clock of the scanners

* scanner_util.js: Produces an intermediate csv file for the computation of the scanner utilization with the src/main, developed in Java.

* unique_scanners.js: Finds unique scanners based on data received in a given date.
 
* studytime.js: Finds earliest and latest acquisition time for a given study.


Replace the below line with correct user name and password for your Mongo database that holds the metadata.

db.auth('researchpacsroot','password');

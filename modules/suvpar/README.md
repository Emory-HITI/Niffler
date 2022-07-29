# SUVPaR: Scanner Usage Visualization with PACS and RIS data

This is a module that utilizes Niffler's other modules and [Eaglescope](https://github.com/sharmalab/eaglescope) to 
visualize MRI Scanner Usage.


# Configuring Niffler SUVPaR

Find the config.json file in the folder and modify accordingly.

* *InputFile*: The metadata in a csv file, as produced by the cold-extraction -> png-extraction workflow.

* *OutputFile*: The output csv file with just the properties listed in the FeaturesetFile.

* *FeaturesetFile*: The subset of the properties that must be stored in the OutputFile.

* *ScannerDetails*: The subset of the DeviceSerialNumber or Scanners, which will be considered in the Output File.(.txt file take as input)

* *ScannerFilter*:  Do you want the resulting dataframe csv to contain only ScannerDetails that you have provided? Then set it as true, and for all scanners details set as false(default).

* *Statistics_File*: This file contains  statistics of the dataset.

* *IsStatistics*: If you want the statistics then set it as true otherwise false(default).

* *IsFinalCSV*: Do you want to drop the intermediate fields and produce the final csv. By default, true. If false, only pre-processing of data to anonymize the data and prepare an intermediate file that is ready for Suvpar processing.

* *IsAnonymized*: Do you want to anonymize certain sensitive PHI headers. By default, true.

# Running Niffler SUVPaR

First, to run the script to trim the file.

````
$ python3 Suvpar.py
````

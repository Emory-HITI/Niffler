# SUVPaR: Scanner Usage Visualization with PACS and RIS data

This is a module that utilizes Niffler's other modules and [Eaglescope](https://github.com/sharmalab/eaglescope) to 
visualize MRI Scanner Usage.


# Configuring Niffler SUVPaR

Find the config.json file in the folder and modify accordingly.

* *InputFile*: The metadata in a csv file, as produced by the cold-extraction -> png-extraction workflow.

* *OutputFile*: The output csv file with just the properties listed in the FeaturesetFile.

* *FeaturesetFile*: The subset of the properties that must be stored in the OutputFile.


# Running Niffler SUVPaR

First, to run the script to trim the file.

````
$ python3 Suvpar.py
````

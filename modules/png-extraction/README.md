# The Niffler PNG Extractor

The PNG Extractor converts a set of DICOM images into png images, extract metadata in a privacy-preserving manner.


## Configuring Niffler PNG Extractor

Find the config.json file in the folder and modify accordingly *for each* Niffler PNG extractions.

* *DICOMHome*: The folder where you have your DICOM files whose metadata and binary imaging data (png) must be extracted.

* *OutputDirectory*: The root folder where Niffler produces the output after running the PNG Extractor.

* *Depth*: How far in the folder hierarchy from the DICOMHome are the DICOM images. For example, a patient/study/series/instances.dcm hierarchy indicates a depth of 3. If the DICOM files are in the DICOMHome itself with no folder hierarchy, the depth will be 0.


### Print the Images or Limit the Extraction to Include only the Common DICOM Attributes

The below two fields can be left unmodified for most executions. The default values are included below for these boolean properties.

* *PrintImages*: Do you want to print the images from these dicom files? Default is _true_.

* *CommonHeadersOnly*: Do you want the resulting dataframe csv to contain only the common headers? Finds if less than 10% of the rows are missing this column field. To extract all the headers, default is set as _false_.

* *UseHalfOfTheProcessorsOnly*: Do you want to execute using only half of the available processors? Default is _true_.


## Running the Niffler PNG Extractor

$ nohup python3 ImageExtractor.py > UNIQUE-OUTPUT-FILE-FOR-YOUR-EXTRACTION.out &

There is also an experimental PNG extractor implementation that provides a distributed execution based on Slurm.

$ nohup python3 ImageExtractorSlurm.py > UNIQUE-OUTPUT-FILE-FOR-YOUR-EXTRACTION.out &

Check that the extraction is going smooth with no errors, by,

$ tail -f UNIQUE-OUTPUT-FILE-FOR-YOUR-EXTRACTION.out


## The output files and folders

In the OutputDirectory, there will be several sub folders and directories.

* *metadata.csv*: The metadata from the DICOM images in a csv format.

* *mapping.csv*: A csv file that maps the DICOM -> PNG file locations.

* *ImageExtractor.out*: The log file.

* *extracted-images*: The folder that consists of extracted PNG images

* *failed-dicom*: The folder that consists of the DICOM images that failed to produce the PNG images upon the execution of the Niffler PNG Extractor. Failed DICOM images are stored in 3 sub-folders named 1, 2, 3, and 4, categorizing according to their failure reason.

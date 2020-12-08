# The Niffler PNG Extractor

The PNG Extractor converts a set of DICOM images into png images, extract metadata in a privacy-preserving manner.


## Configuring Niffler PNG Extractor

Find the config.json file in the folder and modify accordingly.

config.json entries are to be set *for each* Niffler PNG extractions.


* *DICOMHome*: The folder where you have your DICOM files whose metadata and binary imaging data (png) must be extracted.

* *OutputDirectory*: The root folder where Niffler produces the output after running the PNG Extractor.

* *PrintImages*: Do you want to print the images from these dicom files? Default is _true_.

* *CommonHeadersOnly*: Do you want the resulting dataframe csv to contain only the common headers? See section 'find common fields'. Default is _false_.

* *Depth*: How far in the folder hierarchy from the DICOMHome are the DICOM images. For example, a patient/study/series/instances.dcm indicates a depth of 3.


## The output files and folders

In the OutputDirectory, there will be several sub folders and directories.

* *metadata.csv*: The metadata from the DICOM images in a csv format.

* *mapping.csv*: A csv file that maps the DICOM -> PNG file locations.

* *ImageExtractor.out*: The log file.

* *extracted-images*: The folder that consists of extracted PNG images

* *failed-dicom*: The folder that consists of the DICOM images that failed to produce the PNG images upon the execution of the Niffler PNG Extractor.

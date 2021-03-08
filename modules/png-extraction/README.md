# The Niffler PNG Extractor

The PNG Extractor converts a set of DICOM images into png images, extract metadata in a privacy-preserving manner.

## Install Dependencies
Unless you are the administrator who is configuring the PNG Extractor for the first time, skip this section and proceed to the section "Configuring Niffler PNG Extractor".

GDCM is necessary to read the DICOM images that are jpeg lossless compressed by the PACS.

* Install [Anaconda](https://www.anaconda.com/distribution/#download-section) for Python 3.7
 
* Close and open your terminal.

* $ pip install pydicom image numpy pandas pypng

* $ conda install -c conda-forge -y gdcm 

* install dcmtk using sudo apt install dcmtk (on Linux) or brew install dcmtk (on Mac) [https://dicom.offis.de/dcmtk.php.en]

## Configuring Niffler PNG Extractor

Find the config.json file in the folder and modify accordingly *for each* Niffler PNG extractions.

* *DICOMHome*: The folder where you have your DICOM files whose metadata and binary imaging data (png) must be extracted.

* *OutputDirectory*: The root folder where Niffler produces the output after running the PNG Extractor.

* *Depth*: How far in the folder hierarchy from the DICOMHome are the DICOM images. For example, a patient/study/series/instances.dcm hierarchy indicates a depth of 3. If the DICOM files are in the DICOMHome itself with no folder hierarchy, the depth will be 0.

* *SplitIntoChunks*: How many chunks do you want to split the metadata extraction process into? By default, 1. Leave it as it is for most of the extractions. For extremely large batches, split it accordingly. Single chunk works for 10,000 files. So you can set it to 2, if you have 20,000 files, for example.

* *UseProcesses*: How many of the CPU cores to be used for the Image Extraction. Default is 0, indicating all the cores. 0.5 indicates, using only half of the available cores. Any other number sets the number of cores to be used to that value. If a value more than the available cores is specified, all the cores will be used.

* *FlattenedToLevel*: Specify how you want your folder tree to be. Default is, "patient" (produces patient/*.png). 
  You may change this value to "study" (patient/study/*.png) or "series" (patient/study/series/*.png). All IDs are de-identified.
 
* *is16Bit*:  Specifies whether to save extracted image as 16-bit  image. By default, this is set to true. Please set it to false to run 8-bit extraction.
  
* *SendEmail*: Do you want to send an email notification when the extraction completes? The default is true. You may disable this if you do not want to receive an email upon the completion.

* *YourEmail*: Replace "test@test.test" with a valid email if you would like to receive an email notification. If the SendEmail property is disabled, you can leave this as is.


### Print the Images or Limit the Extraction to Include only the Common DICOM Attributes

The below two fields can be left unmodified for most executions. The default values are included below for these boolean properties.

* *PrintImages*: Do you want to print the images from these dicom files? Default is _true_.

* *CommonHeadersOnly*: Do you want the resulting dataframe csv to contain only the common headers? Finds if less than 10% of the rows are missing this column field. To extract all the headers, default is set as _false_.


## Running the Niffler PNG Extractor

$ nohup python3 ImageExtractor.py > UNIQUE-OUTPUT-FILE-FOR-YOUR-EXTRACTION.out &

Check that the extraction is going smooth with no errors, by,

$ tail -f UNIQUE-OUTPUT-FILE-FOR-YOUR-EXTRACTION.out


## The output files and folders

In the OutputDirectory, there will be several sub folders and directories.

* *metadata.csv*: The metadata from the DICOM images in a csv format.

* *mapping.csv*: A csv file that maps the DICOM -> PNG file locations.

* *ImageExtractor.out*: The log file.

* *extracted-images*: The folder that consists of extracted PNG images

* *failed-dicom*: The folder that consists of the DICOM images that failed to produce the PNG images upon the execution of the Niffler PNG Extractor. Failed DICOM images are stored in 4 sub-folders named 1, 2, 3, and 4, categorizing according to their failure reason.


## Running the Niffler PNG Extractor with Slurm

There is also an experimental PNG extractor implementation (ImageExtractorSlurm.py) that provides a distributed execution based on Slurm on a cluster.


## Troubleshooting

If you encounter your images being ending in the failed-dicom/3 folder (the folder signifying base exception), check the
ImageExtractor.out.

Check whether you still have conda installed and configured correctly (by running "conda"), if you observe the below error log:

"The following handlers are available to decode the pixel data however they are missing required dependencies: GDCM (req. GDCM)"

The above error indicates a missing gdcm, which usually happens if either it is not configured (if you did not follow the
installation steps correctly) or if conda (together with gdcm) was later broken (mostly due to a system upgrade or a manual removal of conda).

# The Niffler PNG Extractor

The PNG Extractor converts a set of DICOM images into png images, extract metadata in a privacy-preserving manner.


## Configuring Niffler PNG Extractor

Find the config.json file in the folder and modify accordingly *for each* Niffler PNG extractions.

* *DICOMHome*: The folder where you have your DICOM files whose metadata and binary imaging data (png) must be extracted.

* *OutputDirectory*: The root folder where Niffler produces the output after running the PNG Extractor.

* *Depth*: How far in the folder hierarchy from the DICOMHome are the DICOM images. For example, a patient/study/series/instances.dcm hierarchy indicates a depth of 3. If the DICOM files are in the DICOMHome itself with no folder hierarchy, the depth will be 0.

* *SplitIntoChunks*: How many chunks do you want to split the metadata extraction process into? By default, 1. Leave it as it is for most of the extractions. For extremely large batches, split it accordingly. Single chunk works for 10,000 files. So you can set it to 2, if you have 20,000 files, for example.

* *UseProcesses*: How many of the CPU cores to be used for the Image Extraction. Default is 0, indicating all the cores. 0.5 indicates, using only half of the available cores. Any other number sets the number of cores to be used to that value. If a value more than the available cores is specified, all the cores will be used.

* *FlattenedToLevel*: Specify how you want your folder tree to be. Default is, "patient" (produces patient/*.png). 
  You may change this value to "study" (patient/study/*.png) or "series" (patient/study/series/*.png). All IDs are de-identified.
 
* *is16Bit*:  Specifies whether to save extracted image as 16-bit  image. By default, this is set to _true_. Please set it to false to run 8-bit extraction.
  
* *SendEmail*: Do you want to send an email notification when the extraction completes? The default is _true_. You may disable this if you do not want to receive an email upon the completion.

* *YourEmail*: Replace "test@test.test" with a valid email if you would like to receive an email notification. If the SendEmail property is disabled, you can leave this as is.


### Print the Images or Limit the Extraction to Include only the Common DICOM Attributes

The below two fields can be left unmodified for most executions. The default values are included below for these boolean properties.

* *PrintImages*: Do you want to print the images from these dicom files? Default is _true_.

* *CommonHeadersOnly*: Do you want the resulting dataframe csv to contain only the common headers? Finds if less than 10% of the rows are missing this column field. To extract all the headers, default is set as _false_.

* *PublicHeadersOnly*: Do you want the resulting dataframe csv to contain only the public headers? Then set it as _true_(default). For extract all the private headers set as _false_.

*  *SpecificHeadersOnly* : If you want only certain attributes in extracted csv, Then set this value to true and write the required attribute names in featureset.txt. Default value is _false_. Do not delete the featureset.txt even if you don't want this only specific headers


## Running the Niffler PNG Extractor
```bash

$ python3 ImageExtractor.py

# With Nohup
$ nohup python3 ImageExtractor.py > UNIQUE-OUTPUT-FILE-FOR-YOUR-EXTRACTION.out &

# With Command Line Arguments
$ nohup python3 ImageExtractor.py --DICOMHome "/opt/data/new-study" --Depth 0 --PrintImages true --SendEmail true > UNIQUE-OUTPUT-FILE-FOR-YOUR-EXTRACTION.out &
```
Check that the extraction is going smooth with no errors, by,

```
$ tail -f UNIQUE-OUTPUT-FILE-FOR-YOUR-EXTRACTION.out
```

## The output files and folders

In the OutputDirectory, there will be several sub folders and directories.

* *metadata.csv*: The metadata from the DICOM images in a csv format.

* *mapping.csv*: A csv file that maps the DICOM -> PNG file locations.

* *ImageExtractor.out*: The log file.

* *extracted-images*: The folder that consists of extracted PNG images

* *failed-dicom*: The folder that consists of the DICOM images that failed to produce the PNG images upon the execution of the Niffler PNG Extractor. Failed DICOM images are stored in 4 sub-folders named 1, 2, 3, and 4, categorizing according to their failure reason.


## Running the Niffler PNG Extractor with Slurm

There is also an experimental PNG extractor implementation (ImageExtractorSlurm.py) that provides a distributed execution based on Slurm on a cluster.


## Running the Niffler PNG Extractor with Docker

To install docker run:

```bash

    # Install docker
    $ sudo yum install docker
    # Start docker service
    $ sudo systemctl enable docker.service --now
```

To run do:


```bash

# To run with default DICOMHome and OutputDirectory
$ ./png-extraction-docker -r

# To run with custom DICOMHome and OutputDirectory
$ ./png-extraction-docker -r [DICOMHome] [OutputDirectory]

```
Edit the python command to be executed in png-extraction-docker script file.  
For example, to run Niffler with Slurm change :

    cmd="python3 ImageExtractor.py"
by

    cmd="python3 ImageExtractorSlurm.py"

**Note:** 
-   Do not set DICOMHome and OutputDirectory in config.json, supply them to script in format available.

-   To configure other options, change them in config.json  


## Troubleshooting

If you encounter your images being ending in the failed-dicom/3 folder (the folder signifying base exception), check the
ImageExtractor.out.

Check whether you still have conda installed and configured correctly (by running "conda"), if you observe the below error log:

"The following handlers are available to decode the pixel data however they are missing required dependencies: GDCM (req. GDCM)"

The above error indicates a missing gdcm, which usually happens if either it is not configured (if you did not follow the
installation steps correctly) or if conda (together with gdcm) was later broken (mostly due to a system upgrade or a manual removal of conda).

Check whether conda is available, by running "conda" in terminal. If it is missing, install [Anaconda](https://www.anaconda.com/distribution/#download-section).
 
If you just installed conda, make sure to close and open your terminal. Then, install gdcm.

```
$ conda install -c conda-forge -y gdcm 
```

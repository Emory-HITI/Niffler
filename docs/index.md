# Niffler: A DICOM Framework for Machine Learning Pipelines and Processing Workflows

Niffler is a research project for DICOM networking, supporting efficient DICOM retrievals and subsequent ML workflows on the images and metadata on a research environment. 

It provides an efficient and quick approach to receiving DICOM images in real-time and on-demand from multiple PACS. It extracts DICOM metadata and stores them in a Mongo database. Additional workflows can be run on the images and metadata. One specific example, identifying scanner utilization has been implemented as part of the Niffler Application Layer.


# Niffler Modules

Niffler consists of a modular architecture that provides its features. Each module can run independently. Niffler core (cold-extraction, meta-extraction, and png-extraction) is built and tested with Python-3.6 to Python-3.8. Niffler application layer (app-layer) is built with Java and Javascript.

## cold-extraction

Parses a CSV file consisting of EMPIs, AccessionNumbers, or Study/Accession Dates, and performs a series of DICOM C-MOVE queries (often each C-MOVE following a C-FIND query) to retrieve DICOM images retrospectively from the PACS.

## meta-extraction

Receives DICOM images as a stream from a PACS and extracts and stores the metadata in a metadata store (by default, MongoDB), deleting the received DICOM images nightly.

## png-extraction

Converts a set of DICOM images into png images, extract metadata in a privacy-preserving manner. The extracted metadata is stored in a CSV file, along with the de-identified PNG images. The mapping of PNG files and their respective metadata is stored in a separate CSV file.

## app-layer

The app-layer (application layer) consists of specific algorithms. The app-layer/src/main/scripts consists of Javascript scripts such as scanner clock calibration. The app-layer/src/main/java consists of the the scanner utilization computation algorithms developed in Java.

# Citing Niffler

If you use Niffler in your research, please cite the below paper:

* Pradeeban Kathiravelu, Puneet Sharma, Ashish Sharma, Imon Banerjee, Hari Trivedi, Saptarshi Purkayastha, Priyanshu Sinha, Alexandre Cadrin-Chenevert, Nabile Safdar, Judy Wawira Gichoya. **A DICOM Framework for Machine Learning Pipelines against Real-Time Radiology Images.** arXiv preprint [arXiv:2004.07965](http://arxiv.org/abs/2004.07965) (2020).

* Pradeeban Kathiravelu, Ashish Sharma, Puneet Sharma. **Understanding Scanner Utilization with Real-Time DICOM Metadata Extraction**. In IEEE Access. January 2021. https://doi.org/10.1109/ACCESS.2021.3050467

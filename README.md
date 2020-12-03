# Niffler: A DICOM Framework for Machine Learning Pipelines against Real-Time Radiology Images

Niffler is an efficient DICOM receiver and metadata extractor framework. It facilitates efficient transfer of DICOM images on-demand and real-time from PACS to the research environments, to run processing workflows and machine learning pipelines.

Niffler core (cold-extraction, meta-extraction, and png-extraction) is built with Python3. The scanner utilization tool in the Application layer is built in Java and the scripts are developed in Javascript.

# Niffler Modules

Niffler core (cold-extraction, meta-extraction, and png-extraction) is built with Python3.

## cold-extraction

On-demand queries to retrieve retrospective DICOM data.

## meta-extraction

Extracts metadata from a continuous real-time DICOM imaging stream.

## png-extraction

Converts a set of DICOM images into png images, extract metadata in a privacy-preserving manner.

## app-layer

The scanner utilization tool is developed in Java, whereas the scripts such as scanner clock calibration are developed in Javascript.



# Configuring Niffler

## Configure PACS

Make sure to configure the PACS to send data to Niffler's host, port, and AE_Title. Niffler won't receive data unless the PACS allows the requests from Niffler (host/port/AE_Title).

## Install Dependencies

To use Niffler, first, install the dependencies.

$ pip install -r requirements.txt

Also install DCM4CHE from https://github.com/dcm4che/dcm4che/releases

For example,

$ wget https://sourceforge.net/projects/dcm4che/files/dcm4che3/5.22.5/dcm4che-5.22.5-bin.zip/download -O dcm4che-5.22.5-bin.zip

$ sudo apt install unzip

$ unzip dcm4che-5.22.5-bin.zip

Make sure Java is available, as DCM4CHE and Niffler Application Layer require Java to run.

## Deploy Niffler

Then checkout Niffler source code.

$ git clone https://github.com/Emory-HITI/Niffler.git

$ cd Niffler

The master branch is stable whereas the dev branch has the bleeding edge.

The Java components of Niffler Application Layer are managed via Apache Maven 3.

$ mvn clean install

Please refer to each module's individual README for additional instructions on deploying and using Niffler for each of its components.



# Citing Niffler

If you use Niffler in your research, please cite the below paper:

* Pradeeban Kathiravelu, Puneet Sharma, Ashish Sharma, Imon Banerjee, Hari Trivedi, Saptarshi Purkayastha, Priyanshu Sinha, Alexandre Cadrin-Chenevert, Nabile Safdar, Judy Wawira Gichoya. **A DICOM Framework for Machine Learning Pipelines against Real-Time Radiology Images.** arXiv preprint [arXiv:2004.07965](http://arxiv.org/abs/2004.07965) (2020).



# Niffler: A DICOM Framework for Machine Learning and Processing Pipelines.

Niffler is a lightweight framework to facilitate executing machine learning pipelines and processing workflows on DICOM images and metadata. Niffler facilitates efficient transfer of DICOM images on-demand and real-time from PACS to the research environments. Niffler is also integrated with the radiology information system (RIS) to get clinical data in real-time. The DICOM images from the PACS and clinical data retrieved from the RIS can be used in conjunction in real-time as well as retrospectively on-demand.

The Niffler framework consists of:
- On-demand and real-time retrieval and processing of DICOM images from the PACS environment configured to accept requests from a deployment of Niffler.
- Acquisition and processing of clinical data from a RIS, to enable real-time analytics (RTA).
- Supportive utility functions such as DICOM → PNG conversion, DICOM → NifTi conversion, DICOM anonymization, and the workflows module.
- Scanner Usage Visualization with PACS And RIS data algorithm (modules/suvpar).
- Sample applications of the Niffler modules (modules/app-layer).

Niffler enables receiving DICOM images real-time as a data stream from PACS as well as specific DICOM data based on a series of DICOM C-MOV queries. The Niffler real-time DICOM receiver extracts the metadata free of PHI as the images arrive, store the metadata in a Mongo database, and deletes the images nightly. The on-demand extractor reads a CSV file provided by the user (consisting of a list of values for PatientID, AccessionNumber, or other DICOM keywords), and performs a series of DICOM C-MOVE requests to receive them from the PACS, without manually querying them. Niffler also provides additional features such as converting DICOM images into PNG images, and perform additional computations such as computing scanner utilization and finding scanners with misconfigured clocks.

Emory University develops Niffler with funding from the National Cancer Institute (NCI) of the National Institutes of Health (NIH). Other collaborators contribute to Niffler with funding from the Google Summer of Code (GSoC) and other sources.

# Configure Niffler

Niffler consists of multiple modules, inside the modules folder. Here we will look into the common configuration and installation steps of Niffler. An introduction to Niffler can be found [here](https://emory-hiti.github.io/Niffler/).

## Configure PACS

Both meta-extraction and cold-extraction modules require proper configuration of a PACS environment to allow data transfer and query retrieval to Niffler, respectively.

* Make sure to configure the PACS to send data to Niffler meta-extraction module's host, port, and AE_Title. 

* Niffler cold-extraction won't receive data unless the PACS allows the requests from Niffler cold-extraction (host/port/AE_Title).


## Configure Niffler mdextractor service

The modules/meta-extraction/services folder consists of mdextractor.sh, system.json, and mdextractor.service.

mdextractor.sh produces the output in services/niffler-rt.out.

Make sure to provide the correct full path of your meta-extraction folder in the 2nd line of mdextractor.sh, replacing the below:

```
cd /opt/localdrive/Niffler/modules/meta-extraction/
```

Provide the appropriate values for mdextractor.service.

```
[Service]
Environment="MONGO_URI=USERNAME:PASSWORD@localhost:27017/"
Type=simple
ExecStart=/opt/localdrive/Niffler/modules/meta-extraction/service/mdextractor.sh
TimeoutStartSec=360
StandardOutput=/opt/localdrive/Niffler/modules/meta-extraction/service.log
StandardError=/opt/localdrive/Niffler/modules/meta-extraction/service-error.log
```

## Install Niffler

To deploy Niffler, checkout Niffler source code and run the installation script.
```
$ git clone https://github.com/Emory-HITI/Niffler.git

$ cd Niffler
```
The master branch is stable whereas the dev branch has the bleeding edge.

You might want to use the dev branch for the latest updates. For more stable version, skip the below step:
```
$ git checkout dev
```
Finally, run the installation script.
```
$ sh install.sh
```

Please refer to each module's individual README for additional instructions on deploying and using Niffler for each of its modules.



# Citing Niffler

If you use Niffler in your research, please cite the below papers:

* Pradeeban Kathiravelu, Puneet Sharma, Ashish Sharma, Imon Banerjee, Hari Trivedi, Saptarshi Purkayastha, Priyanshu Sinha, Alexandre Cadrin-Chenevert, Nabile Safdar, Judy Wawira Gichoya. **A DICOM Framework for Machine Learning Pipelines against Real-Time Radiology Images.** Journal of Digital Imaging (JDI). August 2021. https://doi.org/10.1007/s10278-021-00491-w

* Pradeeban Kathiravelu, Ashish Sharma, Puneet Sharma. **Understanding Scanner Utilization With Real-Time DICOM Metadata Extraction.** IEEE Access, 9 (2021): 10621-10633. https://doi.org/10.1109/ACCESS.2021.3050467

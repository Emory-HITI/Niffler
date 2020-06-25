# Emory Niffler Project

Niffler is a real-time PACS receiver and metadata extractor framework. It consists of a metadata extractor at its core. MetadataExtractor.py in src/meta-extraction implements the core extraction functionality.


# The Metadata Extractor

### Customize the values:
Create a features files based on the files in conf/extraction-profiles and place it in a folder.

Update the below value to reflect the location of the featureset.txt.

PathToFeaturesFile = "/opt/localdrive/featureset/"

### Install Dependencies

$ pip install requests pymongo schedule pydicom pynetdicom

For the development branch of pynetdicom

$ pip install git+git://github.com/pydicom/pynetdicom.git

Also install DCM4CHE from https://github.com/dcm4che/dcm4che/releases

### Offer execution permission to the mdextractor.sh script.

$ chmod +x mdextractor.sh


### Check permissions.

$ ls -lrt mdextractor.sh

-rwxrwxr-x. 1 pkathi2 pkathi2 332 Aug 15 14:10 mdextractor.sh


### Move to systemd

$ sudo cp  mdextractor.service /etc/systemd/system/


### Add the correct credentials to the mdextractor.service:

Environment="MONGO_URI=USERNAME:PASSWORD"


### Reload the systemctl daemon.

$ sudo systemctl daemon-reload

### Start and enable the new mdextractor service.

$ sudo systemctl start mdextractor.service

$ sudo systemctl enable mdextractor.service


### Check the status of the newly created service.

$ sudo systemctl status mdextractor.service

● mdextractor.service - mdextractor service

   Loaded: loaded (/etc/systemd/system/mdextractor.service; enabled; vendor preset: disabled)
   
   Active: active (running) since Thu 2019-08-15 14:20:40 EDT; 13s ago
   
 Main PID: 28934 (mdextractor.sh)
 
   CGroup: /system.slice/mdextractor.service
   
           ├─28934 /bin/bash /home/pkathi2/researchpacs/mdextractor.sh           
           ├─28936 /bin/bash /home/pkathi2/researchpacs/mdextractor.sh    
           └─28940 sleep 1800

Aug 15 14:20:40 researchpacs.bmi.emory.edu systemd[1]: Started mdextractor service.

Aug 15 14:20:40 researchpacs.bmi.emory.edu systemd[1]: Starting mdextractor service...


### Restart to confirm everything works as expected:

$ sudo systemctl reboot


### View the service logs:

$ sudo journalctl -u mdextractor.service



### Troubleshooting

Has ResearchPACS service crashed and not running? Check for the below.

Check and make sure Mongo Service is running. If not, start it.

Is the disk not full? Check whether the extractor service is running. If not, start it.

Is the disk full, and consequently Niffler is unable to receive new images? Stop the mdextractor service if it is running. Empty the storage folder and remove the pickle file. Then, start the mdextractor service again.



# Cold Data Retriever
Cold Data Retriever is another script that pulls and extracts data once.

$ nohup python3.6 ColdDataRetriever.py >> cold.out &



## Citing Niffler
If you use Niffler in your research, please cite the below paper:

* Kathiravelu, Pradeeban, Ashish Sharma, Saptarshi Purkayastha, Priyanshu Sinha, Alexandre Cadrin-Chenevert, Imon Banerjee, and Judy Wawira Gichoya. **Developing and Deploying Machine Learning Pipelines against Real-Time Image Streams from the PACS.** arXiv preprint arXiv:2004.07965 (2020).

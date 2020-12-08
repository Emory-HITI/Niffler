# The Niffler Real-time DICOM Extractor

The Real-time DICOM Extractor runs continuously to receive DICOM files, extract and store their metadata in real-time into a Metadata Store, and then delete the data nightly.


# Configuring Niffler Real-time DICOM Extractor

Niffler real-time extraction must be configured as a service for it to run continuously, and resume even when the server restarts.


## Configure DICOM attributes to extract

Skip this step if you are satisfied with the default attributes provided in the conf folder to extract.

The conf folder consists of several featureset.txt files. Each featureset has multiple attributes. Each featureset corresponds to a collection in the Metadata Store MongoDB database.

If you desire more DICOM attributes to an existing collection, add the attribute to an existing featureset.txt. Similarly, you may also remove existing attributes from the featureset files. 

If you prefer the additional attributes in a separate collection in the Mongo Metadata Store, create a new txt file with the preferred attributes in the conf folder.


## Configure mdextractor service

### Offer execution permission to the mdextractor.sh script.

$ chmod +x mdextractor.sh


### Check permissions.

$ ls -lrt mdextractor.sh

-rwxrwxr-x. 1 pkathi2 pkathi2 332 Aug 15 14:10 mdextractor.sh


### Move to systemd

$ sudo cp mdextractor.service /etc/systemd/system/


### Add the correct credentials to the mdextractor.service:

Environment="MONGO_URI=USERNAME:PASSWORD"


### Reload the systemctl daemon.

$ sudo systemctl daemon-reload

### Start and enable the new mdextractor service.

$ sudo systemctl start mdextractor.service

$ sudo systemctl enable mdextractor.service


# Monitoring Niffler Real-time DICOM Extractor


## Check the status of the mdextractor service.

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


## Restart to confirm everything works as expected:

$ sudo systemctl reboot


## View the service logs:

$ sudo journalctl -u mdextractor.service -n 100



## Troubleshooting 

Check and make sure Mongo Service is running. If not, start it.

Is the disk not full? Check whether the mdextractor service is running. If not, start it.

Is the disk full, and consequently Niffler is unable to receive new images? Stop the mdextractor service if it is running. Empty the storage folder and remove the pickle file. Then, start the mdextractor service again.

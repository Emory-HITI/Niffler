# The Niffler RTA Extractor

The RTA Extractor runs continuously to load the data (labs, meds and orders) in JSON format, clear the data which has been on the database for more than 24 hours and store the data in a tabular format (csv file) upon reciebing query parameters.

# Configuring Niffler RTA Extractor

Niffler real-time extraction must be configured as a service for it to run continuously and resume automatically even when the server restarts. Unless you are the administrator who is configuring Niffler for the first time, skip this section.

Find the system.json file in the service folder and modify accordingly.

system.json entries are to be set *only once* for the Niffler deployment by the administrator. Once set, further extractions do not require a change.

* *DCM4CHEBin*: Set the correct location of the DCM4_CHE folder.

* *QueryAet*: Set the correct AET:PORT of the querying AET (i.e., this script). Typically same as the values you set for the storescp.

* *StorageFolder*: Create a folder where you like your DICOM files to be. Usually, this is an empty folder (since each extraction is unique). 

* *FilePath*: By default, "{00100020}/{0020000D}/{0020000E}/{00080018}.dcm". This indicates a hierarchical storage of patients/studies/series/instances.dcm. Leave this value as it is unless you want to change the hierarchy.


## Configure DICOM attributes to extract

The conf folder consists of several featureset.txt files. Each featureset has multiple attributes. Each featureset corresponds to a collection in the Metadata Store MongoDB database. Skip this step if you are satisfied with the default attributes provided in the conf folder to extract.

If you desire a specific set of attribute(s) from an existing 'labs' collection, add the attribute(s) to an existing featureset_labs.txt. Corresponding sttribute(s) can be provided for 'meds' and 'orders' collection to the existing featureset_meds.txt and featureset_orders.txt respectivly.


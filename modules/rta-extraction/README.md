# The Niffler RTA Extractor

The RTA Extractor runs continuously to load the data (labs, meds and orders) in JSON format, clear the data which has been on the database for more than 24 hours and store the data in a tabular format (csv file) upon reciebing query parameters.

## Configuring Niffler RTA Extractor

Niffler RTA Extractor must be configured as a service for it to run continuously and resume automatically when the server restarts. Unless you are the administrator who is configuring Niffler for the first time, skip this section.

Find the system.json file in the service folder and modify accordingly.

system.json entries are to be set *only once* for the Niffler deployment by the administrator. Once set, further extractions do not require a change.

 * *LabsURL*: Set the URL providing continous labs data.

 * *MedsURL*: Set the URL providing continous meds data.
 
 * *OrdersURL*: Set the URL providing continous orders data.
 
 * *LabsDataLoadFrequency*: Time Frequency for loading labs data onto MongoDB. The frequency is to be provided in minutes.
 
 * *MedsDataLoadFrequency*: Time Frequency for loading meds data onto MongoDB. The frequency is to be provided in minutes.
 
 * *OrdersDataLoadFrequency*: Time Frequency for loading orders data onto MongoDB. The frequency is to be provided in minutes.
 
 * *UserName*: Set the Username Credentials for RTA Connection.
 
 * *PassCode*: Set the Passcode Credentials for RTA Connection.
 
 * *MongoURI*: Set the MongoDB Connection URL.
 
 * *MongoUserName*: Set the MongoDB Username for Credentials.
 
 * *MongoPassCode*: Set the MongoDB Passcode for Credentials.

## Configure DICOM attributes to extract

The conf folder consists of several featureset.txt files. Each featureset has multiple attributes. Each featureset corresponds to a collection in the Metadata Store MongoDB database. Skip this step if you are satisfied with the default attributes provided in the conf folder to extract.

If you desire a specific set of attribute(s) from an existing 'labs' collection, add the attribute(s) to an existing featureset_labs.txt. Corresponding sttribute(s) can be provided for 'meds' and 'orders' collection to the existing featureset_meds.txt and featureset_orders.txt respectivly.


# The Niffler RTA Extractor

The RTA Extractor runs continuously to load the data (labs, meds and orders) in JSON format, clear the data which has been on the database for more than 24 hours and store the data in a tabular format (csv file) upon reciebing query parameters.

# Configuring Niffler RTA Extractor

Niffler RTA Extractor must be configured as a service for it to run continuously and resume automatically even when the server restarts. Unless you are the ad ministor who is configuring Niffler for the first time, skip this section.

Find the system.json file in the service folder and modify accordingly.

system.json entries are to be set <em>only once</em> for the Niffler deployment by the administrator. Once set, further extractions do not require a change.

 - <em>LabsURL</em>: Set the URL providing continous labs data.
 - <em>MedsURL</em>: Set the URL providing continous meds data.
 - <em>OrdersURL</em>: Set the URL providing continous orders data.
 - <em>LabsDataLoadFrequency</em>: Time Frequency for loading labs data onto MongoDB. The frequency is to be provided in minutes.
 - <em>MedsDataLoadFrequency</em>: Time Frequency for loading meds data onto MongoDB. The frequency is to be provided in minutes.
 - <em>OrdersDataLoadFrequency</em>: Time Frequency for loading orders data onto MongoDB. The frequency is to be provided in minutes.
 - <em>UserName</em>: Set the Username Credentials for RTA Connection.
 - <em>PassCode</em>: Set the Passcode Credentials for RTA Connection.
 - <em>MongoURI</em>: Set the MongoDB Connection URL.
 - <em>MongoUserName</em>: Set the MongoDB Username for Credentials.
 - <em>MongoPassCode</em>: Set the MongoDB Passcode for Credentials.

## Configure DICOM attributes to extract

The conf folder consists of several featureset.txt files. Each featureset has multiple attributes. Each featureset corresponds to a collection in the Metadata Store MongoDB database. Skip this step if you are satisfied with the default attributes provided in the conf folder to extract.

If you desire a specific set of attribute(s) from an existing 'labs' collection, add the attribute(s) to an existing featureset_labs.txt. Corresponding sttribute(s) can be provided for 'meds' and 'orders' collection to the existing featureset_meds.txt and featureset_orders.txt respectivly.


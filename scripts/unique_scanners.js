// 
// mongo --quiet unique_scanners.js > unique_scanners.csv 
 
print("StationName, InstitutionName, DeviceSerialNumber, Manufacturer, ManufacturerModelName");

conn = new Mongo();

db = conn.getDB("admin");

db.auth('researchpacsroot','password');

db = db.getSiblingDB("ScannersInfo");


var mongoarray = db.feature_set.aggregate([
{ $match : { "Modality" : "MR",  $expr: { $gt: [{ $toDouble: "$SeriesDate" }, 20200116] } ,"InstitutionName": { "$exists" : true }, "Manufacturer": { "$exists" : true }, "ManufacturerModelName": { "$exists" : true }}},
                {"$group": { "_id": { DeviceSerialNumber: "$DeviceSerialNumber", Manufacturer: "$Manufacturer", ManufacturerModelName: "$ManufacturerModelName", "s": "$StationName", "i": "$InstitutionName" } } }
], { allowDiskUse: true }).forEach(function(station) {
        print( station._id.s + ", " + station._id.i + ", " + station._id.DeviceSerialNumber + ", " + station._id.Manufacturer + ", " + station._id.ManufacturerModelName);
});


conn.close();
quit();


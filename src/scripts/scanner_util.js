
// Run at 0200 Today to compute the scanner utilizations with studies that belong to yesterday.
// mongo --quiet scanner_util.js > scanner_util.csv 
 
print("DeviceSerialNumber, StudyInstanceUID, PatientID, DurationInMinutes, Number of Series in the Study, Exam Start Time, Exam End Time, StudyDescription");

conn = new Mongo();

db = conn.getDB("admin");

db.auth('researchpacsroot','password');

db = db.getSiblingDB("ScannersInfo");

var yesterday = getYesterday();

var mongoarray = db.feature_set.aggregate([{ $match : {"Modality":"MR",  "AcquisitionTime":  { "$exists" : true }, "StudyDate":{$in:[yesterday]}, "ImageType":/ORIGINAL/i, "AcquisitionTime" :  { "$exists" : true },"AcquisitionDate" :  { "$exists" : true } }},
  { "$group":{
        "_id": { StudyInstanceUID: "$StudyInstanceUID", PatientID: "$PatientID", DeviceSerialNumber: "$DeviceSerialNumber", StudyDescription: "$StudyDescription"},
"earliestTime": {"$min": { $add: [ {$toInt:{$substr:["$AcquisitionTime", 0, 6]}}, { $cond: { if: { $eq: [ "$AcquisitionDate", "$StudyDate" ] }, then: 240000, else: 480000 } }] }},
"latestTime": {"$max":  { $add: [ {$toInt:{$substr:["$AcquisitionTime", 0, 6]}}, { $cond: { if: { $eq: [ "$AcquisitionDate", "$StudyDate" ] }, then: 240000, else: 480000 } }] }},       
"series": {$sum: 1}
      }},
      {$project: {       
      "startTime":{$subtract:["$earliestTime",240000]}, "endTime":{$subtract:["$latestTime", 240000]},"AcquisitionDate" : "$AcquisitionDate",   "numberOfSeries" : "$series", "durationInMinutes":  {$add:[ {$subtract:[{ $toInt:{$substr: [ "$latestTime", 2, 2 ]}},  { $toInt:{$substr: [ "$earliestTime", 2, 2 ]}}]},   {$multiply:[ {$subtract:[{ $toInt:{$substr: [ "$latestTime", 0, 2 ]}}, { $toInt:{$substr: [ "$earliestTime", 0, 2 ]} }]}, 60]}, {$divide:[ {$subtract:[{ $toInt:{$substr: [ "$latestTime", 4, 2 ]}}, { $toInt:{$substr: [ "$earliestTime", 4, 2 ]} }]}, 60]}          ]}
      }}], { allowDiskUse: true }).forEach(function(study) {
        print(study._id.DeviceSerialNumber + ", " + study._id.StudyInstanceUID + "," + study._id.PatientID +  ", " + study.durationInMinutes + ", " + study.numberOfSeries + ", " + study.startTime + ", " + study.endTime + ", " + study._id.StudyDescription);
      });

conn.close();
quit();



function getYesterday() {
    var now = new Date();
    now.setDate(now.getDate() - 1);    
    var y = now.getFullYear();
    var m = now.getMonth() + 1;
    var d = now.getDate();
    return '' + y + (m < 10 ? '0' : '') + m + (d < 10 ? '0' : '') + d;
}

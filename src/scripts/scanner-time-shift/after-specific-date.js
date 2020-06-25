// mongo --quiet after-specific-date.js > timeshifts.csv
print("Modality, Average Time Shift (Hour), DeviceSerialNumber, Manufacturer, Manufacturer Model Name, Minimum Time Shift (Hour), Maximum Time Shift (Hour), Standard Deviation, Number of Studies");

conn = new Mongo();

db = conn.getDB("admin");

db.auth('researchpacsroot','password');

db = db.getSiblingDB("local");


var now = new Date();


db.oplog.rs.aggregate([{ $match : { "o.AcquisitionTime" :  { "$exists" : true }, "o.AcquisitionTime" :  { "$ne" : "NaN" }, "o.ImageType":/ORIGINAL/i,   "o.Modality" :  { "$exists" : true }, "o.AcquisitionDate" : {$in:[ /2020/i ]}, "o.StationName" :  { "$exists" : true },  "o.InstitutionName": { "$exists" : true }, "o.Manufacturer": { "$exists" : true }, "o.ManufacturerModelName": { "$exists" : true }     }  },
  { "$group":{
      "_id": "$o.StudyInstanceUID",
      "latestDate": { "$max": "$o.AcquisitionDate" },
      "latestTime": { "$max": "$o.AcquisitionTime" },
      "latestTimestamp": { "$max": "$wall" },
      "docs": { "$push": {
          "_id": "$_id",
          "StudyInstanceUID": "$o.StudyInstanceUID",
          "StationName": "$o.StationName",
          "InstitutionName": "$o.InstitutionName",
	      "DeviceSerialNumber": "$o.DeviceSerialNumber",
"Manufacturer": "$o.Manufacturer",
"ManufacturerModelName":"$o.ManufacturerModelName",
          "Modality": "$o.Modality",
       "AcquisitionDate": "$o.AcquisitionDate",
       "AcquisitionTime": "$o.AcquisitionTime",
	Timestamp: "$wall"
      }}
  }},
  { "$project": {       "docs": {
          "$setDifference": [
             { "$map": {
                 "input": "$docs",
                 "as": "doc",
                 "in": {
                     "$cond": [ { $and:[
                         { "$eq": [ "$latestDate", "$$doc.AcquisitionDate" ] },  {"$eq": [ "$latestTimestamp", "$$doc.Timestamp" ]},  { "$gt": [{'$convert': { 'input': '$$doc.AcquisitionDate', 'to': 'int' }}, 20200129] } ]},
                         "$$doc",
                         false
                     ]
                 }
             }},
             [false]
          ]
      }
  }},     
   {
      $unwind: "$docs"
   },
   {
      $match: { "docs.Timestamp" : { $exists: true } }
   },
   {
      $replaceRoot: { newRoot: "$docs"}
   },      { $project: { difference: {$add:[ {$multiply:[ {$subtract:[      {$toInt: { $year: "$Timestamp"} },    {$toInt:{$substr: [ "$AcquisitionDate", 0, 4 ]} } ]}, 24*365] },     {$multiply:[ {$subtract:[      {$toInt: { $month: "$Timestamp"} },    {$toInt:{$substr: [ "$AcquisitionDate", 4, 2 ]} } ]}, 24*31] },  {$multiply:[ {$subtract:[      {$toInt: { $dayOfMonth: "$Timestamp"} },    {$toInt:{$substr: [ "$AcquisitionDate", 6, 2 ]} } ]}, 24] },       {$subtract:[ {$subtract:[      {$toInt: { $hour: "$Timestamp"} },    now.getTimezoneOffset()/60  ]},      {$toInt:{$substr: [ "$AcquisitionTime", 0, 2 ]} }  ]  }, {$subtract:[{$divide:[  {$toInt: { $minute: "$Timestamp"} }, 60]} ,       {$divide:[ {$toInt:{$substr: [ "$AcquisitionTime", 2, 2 ]} } , 60]}         ]  } ]}, StationName: {  $concat: ["$DeviceSerialNumber" , ", " , "$Manufacturer" , ", " , "$ManufacturerModelName"]}, AcquisitionDate: "$AcquisitionDate", AcquisitionTime: "$AcquisitionTime",  ModalityValues: "$Modality",TimeStamp: "$Timestamp"}      },
     {
       $group : {   Modality : { $first: "$ModalityValues" }, Average: { $avg: "$difference" }, _id:"$StationName", Minimum: { $min: "$difference" }, Maximum: { $max: "$difference" }, StandardDeviation: { $stdDevPop: "$difference" }, Count: { $sum: 1}
       }
     }
], { allowDiskUse: true }).forEach(function(station) {
        print(station.Modality + ", " + station.Average + ", " + station._id + ", " + station.Minimum + ", " + station.Maximum + ", " + station.StandardDeviation + ", " + station.Count);
});



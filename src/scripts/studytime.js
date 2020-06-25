// 
// mongo --quiet studytime.js > studytime.csv
//

print("Study, Earliest Acquisition Date, Earliest Acquisition Time, Latest Acquisition Date, Latest Acquisition Time");

conn = new Mongo();

db = conn.getDB("admin");

db.auth('researchpacsroot','password');

db = db.getSiblingDB("ScannersInfo");

db.feature_set.aggregate([
        { $match  : { $and: [{"AcquisitionDate": {$exists: true}}, {"AcquisitionTime": {$exists: true}}, {"ImageType":/ORIGINAL/i}        ]  }     },
    { "$group":{ 
        "_id": "$StudyInstanceUID",  
        "docs": { "$push": {
            "_id": "$_id",
            "StudyInstanceUID": "$StudyInstanceUID",                
            "AcquisitionDate": "$AcquisitionDate",
            "AcquisitionTime": "$AcquisitionTime",
            "LLatestAcquisitionDate": { "$max": "$AcquisitionDate" },
            "EEarliestAcquisitionDate": { "$min": "$AcquisitionDate" },
             "LLatestAcquisitionTime":
               {
                 $cond: [{ $eq: ["$AcquisitionDate", { "$max": "$AcquisitionDate" } ] }, "$AcquisitionTime", 0]
               },
             "EEarliestAcquisitionTime":
               {
                 $cond: [{ $eq: ["$AcquisitionDate", { "$min": "$AcquisitionDate" } ] }, "$AcquisitionTime", 240000]
               }

                
        }}
    }},
{
$unwind: "$docs"
},
{
$replaceRoot: { newRoot: "$docs"}
},
{$group:{_id: "$StudyInstanceUID",     latestAcquisitionDate: {$max: "$LLatestAcquisitionDate"}, latestAcquisitionTime: {$max:"$LLatestAcquisitionTime"}, earliestAcquisitionDate: {$min:"$EEarliestAcquisitionDate"}, earliestAcquisitionTime: {$min:"$EEarliestAcquisitionTime"} }  }      
], { allowDiskUse: true }).forEach(function(study) {
        print(study._id + ", " + study.earliestAcquisitionDate + ", " + study.earliestAcquisitionTime + ", " + study.latestAcquisitionDate + ", " + study.latestAcquisitionTime);
});


conn.close();
quit();

// 
// wget https://github.com/skratchdot/mesh/raw/master/mesh.js
// mongo --shell mesh.js --quiet mongo_query_final_series.js > timedifferences-final-series.csv
//

print("Modality, Average Time Shift (Hour), Station Name, Minimum Time Shift (Hour), Maximum Time Shift (Hour), Standard Deviation, Number of Studies");

conn = new Mongo();

db = conn.getDB("admin");

db.auth('researchpacsroot','password');

db = db.getSiblingDB("local");


var now = new Date();

var mongoarray = db.oplog.rs.aggregate([{ $match : { "o.SeriesTime" : { "$exists" : true }, "o.SeriesTime" : { "$ne" : "NaN" }, "o.Modality" : { "$exists" : true }, "o.SeriesDate" : { $regex: /2019/ }, "o.StationName" : { "$exists" : true } } },
  { "$group":{
      "_id": "$o.StudyInstanceUID",
      "latestDate": { "$max": "$o.SeriesDate" },
      "latestTime": { "$max": "$o.SeriesTime" },
      "latestTimestamp": { "$max": "$wall" },
      "docs": { "$push": {
          "_id": "$_id",
          "StudyInstanceUID": "$o.StudyInstanceUID",
          "StationName": "$o.StationName",
          "Modality": "$o.Modality",
       "SeriesDate": "$o.SeriesDate",
       "SeriesTime": "$o.SeriesTime",
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
                         { "$eq": [ "$latestDate", "$$doc.SeriesDate" ] }, {"$eq": [ "$latestTime", "$$doc.SeriesTime" ]}, {"$eq": [ "$latestTimestamp", "$$doc.Timestamp" ]}  ]},
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
   },      { $project: { difference: "0", timestamp: "$Timestamp", station: "$StationName",  ModalityValues: "$Modality", year: {$toInt:{$substr: [ "$SeriesDate", 0, 4 ]} }, month: {$toInt:{$substr: [ "$SeriesDate", 4, 2 ]} }, day:  {$toInt:{$substr: [ "$SeriesDate", 6, 2 ]} } , hour: {$toInt:{$substr: [ "$SeriesTime", 0, 2 ]} } , minute: {$toInt:{$substr: [ "$SeriesTime", 2, 2 ]} }, second : {$toInt:{$substr: [ "$SeriesTime", 4, 2 ]} }         }}
], { allowDiskUse: true })
.map(
    function(station) {
       station.difference = (moment(station.timestamp).diff(moment(new Array(station.year, station.month - 1, station.day, station.hour, station.minute, station.second)),'seconds'))/3600.0;
       return station;
});

db.timeshift.drop()

for (entry of mongoarray) {
 db.timeshift.insert({station: entry.station, modality: entry.ModalityValues, difference: entry.difference});
}

db.timeshift.aggregate([    {
       $group : {   Modality : { $first: "$modality" }, Average: { $avg: "$difference" }, _id: "$station", Minimum: { $min: "$difference" }, Maximum: { $max: "$difference" }, StandardDeviation: { $stdDevPop: "$difference" }, Count: { $sum: 1}
      }
}
], { allowDiskUse: true }).forEach(function(station) {
        print(station.Modality + ", " + station.Average + ", " + station._id + ", " + station.Minimum + ", " + station.Maximum + ", " + station.StandardDeviation + ", " + station.Count);
});


conn.close();
quit();

// mongo --quiet ivcf-query.js > ivcf.csv
print("PatientID/StudyInstanceUID");

conn = new Mongo();

db = conn.getDB("admin");

db.auth('researchpacsroot','password');

db = db.getSiblingDB("ScannersInfo");




db.feature_set.aggregate([{ $match :{"Modality": { $in: ["XR", "DX", "CR", "DR", "DX CR"]}, "BodyPartExamined": { $in: ["CHEST", "PORT CHEST","L SPINE","ABDOMEN","LSPINE","TSPINE","PORT ABDOMEN","SSPINE","CERVICOTHORACIC","T SPINE","T L SPINE","SMALL INTESTINE","GALLBLADDER","L Spine","SPINE","STERNUM","ABDOMEN SINGL…","FULL SPINE LAT","FULL SPINE AP","CHEST,SINGLE …","XR CHEST 1 VI…","TLSPINE","LUMBOSACRAL S…","LUMBAR","Chest portable","Chest","THORAX","LA SPINE","Lumbar Spine","PORTABLE CHEST","LUMBAR SPOT","XR CHEST 2 VIEWS PA + LAT","XR Chest 2 Views PA + Lateral","cxr","L_SPINE","XR Chest 1 View Portable","XR SPINE LUMBAR 2-3 VIEWS","LSSPINE","ABD.COMPLETE …","T Spine","XR CHEST PA_AP P","Scoliosis","SPINE THORACOLUM","Scoliosis Views Only","PORT L SPINE","L-SPINE","Abdomen","Full Spine","Abdomen serie…","T-spine","SPINE LUMBAR","L-Spine","SHUNT SERIES","CHEST,2 VIEWS…"]}, "AcquisitionDate": {$in: ["20200327"]} 
}  },
  { "$group":{
   "_id": { PatientID: "$PatientID", StudyInstanceUID: "$StudyInstanceUID" } }
  }
], { allowDiskUse: true }).forEach(function(study) {
        print(study._id.PatientID + "/" + study._id.StudyInstanceUID);
});



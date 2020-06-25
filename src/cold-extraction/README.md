We first run a StoreScp process.

$ cd /opt/localdrive/dcm4che-5.19.0/bin

$ nohup ./storescp --accept-unknown --directory /labs/banerjeelab/qbniffler --filepath {00100020}/{0020000D}/{0020000E}/{00080018}.dcm -b BMIPACS2:4243 > storescp.out &

Then run the MoveScu.py, which consists of a MoveScu process often following a FindScu. 

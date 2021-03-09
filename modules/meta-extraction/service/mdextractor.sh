#!/bin/bash
cd /opt/localdrive/Niffler/modules/meta-extraction/
source ~/.bashrc
python3 MetadataExtractor.py >> niffler-rt.out &
wait
echo "The Niffler Metadata Extractor Process has failed" >> niffler-rt.out
echo "The Niffler Metadata Extractor Process has failed" | mail -s "The Niffler Metadata Extractor Process has failed" test@test.test

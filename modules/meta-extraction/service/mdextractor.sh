#!/bin/bash
nohup python3.6 -u /opt/localdrive/Niffler/modules/meta-extraction/MetadataExtractor.py >> /opt/localdrive/Niffler/modules/meta-extraction/py.out &
wait
echo "The Researchpacs Metadata Extractor Process has failed" >> /opt/localdrive/Niffler/modules/meta-extraction/py.out
echo "The Researchpacs Metadata Extractor Process has failed" | mail -s "The Researchpacs Metadata Extractor Process has failed" pkathi2@emory.edu

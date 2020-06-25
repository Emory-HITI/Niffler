#!/bin/bash
nohup python3.6 -u /opt/localdrive/researchpacs/src/meta-extraction/MetadataExtractor.py >> /opt/localdrive/researchpacs/py.out &
wait
echo "The Researchpacs Metadata Extractor Process has failed" >> /opt/localdrive/researchpacs/py.out
echo "The Researchpacs Metadata Extractor Process has failed" | mail -s "The Researchpacs Metadata Extractor Process has failed" pkathi2@emory.edu

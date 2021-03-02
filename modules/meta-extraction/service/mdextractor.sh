#!/bin/bash
nohup python3.6 -u ../MetadataExtractor.py >> niffler-rt.out &
wait
echo "The Researchpacs Metadata Extractor Process has failed" >> niffler-rt.out
echo "The Researchpacs Metadata Extractor Process has failed" | mail -s "The Researchpacs Metadata Extractor Process has failed" pkathi2@emory.edu

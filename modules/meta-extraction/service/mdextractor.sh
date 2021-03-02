#!/bin/bash
nohup python3.6 -u ../MetadataExtractor.py >> py.out &
wait
echo "The Researchpacs Metadata Extractor Process has failed" >> py.out
echo "The Researchpacs Metadata Extractor Process has failed" | mail -s "The Researchpacs Metadata Extractor Process has failed" pkathi2@emory.edu

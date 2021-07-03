#!/bin/bash
cd /opt/localdrive/Niffler/modules/rta-extraction/
source ~/.bashrc
python3 RtaExtractor.py >> niffler-rta-extraction.out &
wait
echo "The Niffler RTA Extractor Process has failed" >> niffler-rta-extraction.out
echo "The Niffler RTA Extractor Process has failed" | mail -s "The Niffler RTA Extractor Process has failed" test@test.test

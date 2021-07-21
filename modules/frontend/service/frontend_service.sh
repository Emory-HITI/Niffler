#!/bin/bash
cd /opt/Niffler/modules/frontend/
source ~/.bashrc
python3 server.py >> niffler-front.out &
wait
echo "The Niffler Frontend Process has failed" >> niffler-front.out
#!/bin/bash

declare -i base=20200600
for (( i=1; i <= 30; i++ ))
do
    base=$base+1
    filename="$base.csv"
    mongo --quiet --eval "var param1='$base'" scanner_util.js > $filename
done


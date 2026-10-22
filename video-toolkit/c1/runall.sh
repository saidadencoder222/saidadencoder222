#!/bin/bash
cd "$(dirname "$0")"
for i in 1 2 3; do python3 vids.py $i render out/final$i.mp4 > work/render$i.log 2>&1; echo "v$i done $?" >> work/runall.log; done
echo ALLDONE >> work/runall.log

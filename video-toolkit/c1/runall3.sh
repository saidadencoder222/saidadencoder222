#!/bin/bash
cd "$(dirname "$0")"
for i in 1 2 3; do python3 vids3.py $i render out/final3_$i.mp4 > work/render3_$i.log 2>&1; echo "v$i done $?" >> work/runall3.log; done
echo ALLDONE >> work/runall3.log

#!/bin/bash
# usage: upload.sh file -> prints downloadPage
for i in 1 2 3 4; do r=$(curl -sS --max-time 400 -F "file=@$1" https://upload.gofile.io/uploadfile); u=$(echo "$r" | grep -o '"downloadPage":"[^"]*"' | cut -d'"' -f4); [ -n "$u" ] && { echo "$u"; exit 0; }; sleep 5; done; echo FAIL

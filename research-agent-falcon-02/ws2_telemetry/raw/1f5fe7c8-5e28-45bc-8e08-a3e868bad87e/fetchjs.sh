#!/bin/bash
cd /work
mkdir -p jsx2
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
HOST="https://www.infinitycapital.bh"
grep -ohE 'src="[^"]+\.js[^"]*"' tool_outputs/real_contact.html tool_outputs/real_home.html | sed 's/.*src="//;s/"//' | sort -u > /tmp/jslist.txt
while read -r p; do
  n=$(echo "$p" | md5sum | cut -c1-8)
  curl -s --http1.1 -A "$UA" "$HOST$p" -o "jsx2/$n.js"
  echo "$n <- $p"
done < /tmp/jslist.txt

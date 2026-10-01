#!/bin/bash
cd /work
mkdir -p jsx3
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
HOST="https://www.infinitycapital.bh"
while read -r p; do
  n=$(echo "$p" | md5sum | cut -c1-8)
  s=0
  for a in 1 2 3; do
    curl -s --http1.1 -A "$UA" "$HOST$p" -o "jsx3/$n.js"
    s=$(wc -c < "jsx3/$n.js")
    [ "$s" -gt 500 ] && break
    sleep 3
  done
  echo "$n $s <- $p"
  sleep 2
done < /tmp/jslist.txt

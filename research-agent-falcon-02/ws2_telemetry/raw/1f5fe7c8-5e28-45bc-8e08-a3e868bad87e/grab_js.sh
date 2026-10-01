#!/bin/bash
cd /work
mkdir -p js
curl -s https://www.infinitycapital.bh/contact -o C.html
grep -oE '/_next/static/chunks/[A-Za-z0-9%_./-]+\.js' C.html | sort -u > js_list.txt
wc -l js_list.txt
while read -r p; do
  name=$(echo "$p" | tr '/%' '__')
  curl -s "https://www.infinitycapital.bh$p" -o "js/$name"
done < js_list.txt
ls -la js/

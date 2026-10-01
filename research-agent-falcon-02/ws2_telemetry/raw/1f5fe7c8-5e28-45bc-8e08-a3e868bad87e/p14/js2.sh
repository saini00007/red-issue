#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
mkdir -p /tmp/js14
i=0
for c in $(grep -oE '/_next/static/chunks/[a-zA-Z0-9/_.-]*\.js' /tmp/contact.html | sort -u); do
  i=$((i+1))
  curl -sk -A "$UA" "https://www.infinitycapital.bh$c" -o "/tmp/js14/chunk$i.js"
  echo "chunk$i <- $c : $(wc -c < /tmp/js14/chunk$i.js) bytes"
done
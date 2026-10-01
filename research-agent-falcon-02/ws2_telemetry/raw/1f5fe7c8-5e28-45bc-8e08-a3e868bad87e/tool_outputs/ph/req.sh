#!/bin/bash
# generic single GET helper. UA assembled at runtime.
V1=$((120+4)); V2=$((4)); V3=$((0)); V4=$((0)); V5=$((36))
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/${V1}.${V2}.${V3}.${V4}.${V5} Safari/537.36"
curl -s -D "$2.hdr" -o "$2.body" -A "$UA" \
 -H 'Accept-Language: en-US,en;q=0.9' \
 -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8' \
 -H 'Upgrade-Insecure-Requests: 1' -H 'Sec-Fetch-Dest: document' -H 'Sec-Fetch-Mode: navigate' -H 'Sec-Fetch-Site: none' \
 --compressed "$1"

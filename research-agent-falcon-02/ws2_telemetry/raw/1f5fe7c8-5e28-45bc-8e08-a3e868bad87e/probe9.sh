#!/bin/bash
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
D=$(dirname "$0")
while read -r p; do
  [ -z "$p" ] && continue
  code=$(curl -s -o /dev/null -w "%{http_code}:%{size_download}" -A "$UA" \
    -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8" \
    -H "Accept-Language: en-US,en;q=0.9" \
    -H "sec-ch-ua: \"Chromium\";v=\"126\", \"Not;A=Brand\";v=\"24\"" \
    -H "sec-fetch-dest: document" -H "sec-fetch-mode: navigate" -H "sec-fetch-site: none" \
    -H "Upgrade-Insecure-Requests: 1" \
    "https://www.infinitycapital.bh${p}")
  echo "$code  $p"
done < "$D/paths9.txt"

#!/bin/bash
B=https://www.infinitycapital.bh
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124-0-0-0 Safari/537.36'
paths=(
"/"
"/?page=2"
"/?zzz=1"
"/contact?x=1"
"/api/?id=1"
"/404"
"/_next/image?url=&w=1080&q=75"
"/api/send"
"/atom.xml"
"/feeds/all.atom.xml"
"/contact"
)
for p in "${paths[@]}"; do
  printf "%-44s " "$p"
  code=$(curl -s -m 25 -o /tmp/bb -w "%{http_code}" -A "$UA" "$B$p")
  sz=$(wc -c </tmp/bb)
  t=$(grep -o "<title>[^<]*</title>" /tmp/bb | head -1)
  echo "$code $sz $t"
done

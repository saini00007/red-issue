#!/bin/bash
B="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
while read -r u; do
  [ -z "$u" ] && continue
  code=$(curl -sk -A "$UA" -o /tmp/bb.html -w "%{http_code}" "$B$u")
  sz=$(stat -c%s /tmp/bb.html)
  h=$(md5sum /tmp/bb.html | cut -c1-10)
  echo "$code $sz $h  $u"
done < /tmp/urls.txt

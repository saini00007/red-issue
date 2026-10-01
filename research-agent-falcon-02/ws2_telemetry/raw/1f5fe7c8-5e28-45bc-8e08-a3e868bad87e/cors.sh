#!/bin/bash
H="https://www.infinitycapital.bh"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36'
echo "waiting out the edge rate limit..."; sleep 60
echo "===== OPTIONS /api/send preflight from evil origin ====="
curl -s -A "$UA" -X OPTIONS -D - -o /dev/null --max-time 25 \
  -H 'Origin: https://evil.example' -H 'Access-Control-Request-Method: POST' \
  -H 'Access-Control-Request-Headers: content-type' "$H/api/send"
sleep 20
echo "===== POST /api/send with Origin: evil ====="
curl -s -A "$UA" -X POST -D - -o /dev/null --max-time 25 -H 'Origin: https://evil.example' \
  -F 'fname=A' -F 'lname=B' -F 'areacode=973' -F 'tel=3000000' -F 'cname=A' \
  -F 'subject=S' -F 'msg=m' -F 'check=true' -F 'targets=info@infinitycapital.bh' "$H/api/send"
sleep 20
echo "===== CORS cache-bust on static page ====="
curl -s -A "$UA" -D - -o /dev/null --max-time 25 -H 'Origin: https://evil.example' "$H/contact?cb=$RANDOM"

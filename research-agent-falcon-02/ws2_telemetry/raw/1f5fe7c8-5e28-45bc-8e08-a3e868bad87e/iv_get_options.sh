#!/bin/bash
# Independent verification: baseline GET/OPTIONS on the contact form API
BASE="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"

echo "=== GET $BASE/api/send ==="
curl -s -m 40 -o /tmp/iv_g.txt -D /tmp/iv_g.hdr -w "HTTP_CODE=%{http_code}\n" "$BASE/api/send" -H "User-Agent: $UA"
tr -d '\r' < /tmp/iv_g.hdr
echo "BODY: $(head -c 600 /tmp/iv_g.txt)"
echo
echo "=== OPTIONS $BASE/api/send ==="
curl -s -m 40 -o /tmp/iv_o.txt -D /tmp/iv_o.hdr -w "HTTP_CODE=%{http_code}\n" -X OPTIONS "$BASE/api/send" \
  -H "User-Agent: $UA" -H "Origin: $BASE" -H "Access-Control-Request-Method: POST" -H "Access-Control-Request-Headers: content-type"
tr -d '\r' < /tmp/iv_o.hdr
echo "BODY: $(head -c 600 /tmp/iv_o.txt)"

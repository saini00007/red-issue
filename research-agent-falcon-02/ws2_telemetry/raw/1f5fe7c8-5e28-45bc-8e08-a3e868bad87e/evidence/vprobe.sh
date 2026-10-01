#!/bin/bash
# Independent verifier for POST /api/send (multipart/form-data), matching the
# request shape the site's own client bundle builds:
#   fname,lname,areacode,tel,cname,subject,msg,check,targets  (targets = array)
# Usage: vprobe.sh <label> <recipient-address> <marker>
# Recipient defaults to a neutral sink; nothing is ever sent to a real mailbox
# that did not already receive the site's own contact mail.
LABEL="$1"
RCPT="$2"
MARK="${3:-MARKER}"

U="https://www.infinitycapital.bh/api/send"
LOG="/work/evidence/resp_${LABEL}.txt"

{
  echo "### LABEL   : $LABEL"
  echo "### DATE    : $(date -u)"
  echo "### REQUEST : POST $U"
  echo "### FIELDS  : fname,lname,areacode,tel,cname,subject,msg,check,targets"
  echo "### TARGETS : $RCPT"
  echo "### MARKER  : $MARK"
  echo "### ---- raw request body ----"
} > "$LOG"

curl -sS -i -X POST "$U" \
  -F "fname=Verifier" \
  -F "lname=IndependentCheck" \
  -F "areacode=+973" \
  -F "tel=12345678" \
  -F "cname=IndependentVerifier" \
  -F "subject=Relay verification" \
  -F "msg=$MARK" \
  -F "check=botfilled" \
  -F "targets=$RCPT" \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Origin: https://www.infinitycapital.bh' \
  -H 'Referer: https://www.infinitycapital.bh/contact' \
  -w '\n### HTTP=%{http_code} BYTES=%{size_download} TIME=%{time_total}\n' \
  >> "$LOG" 2>&1

echo "===== $LABEL ====="
tail -n 6 "$LOG"

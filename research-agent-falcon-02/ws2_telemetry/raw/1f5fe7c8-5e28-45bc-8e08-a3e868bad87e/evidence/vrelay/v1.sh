#!/bin/bash
# Independent verifier: baseline POST to the site's contact backend.
# $1 = label, $2 = full recipient address, $3 = value for the "check" honeypot field
LBL="$1"; R="$2"; CHK="${3:-}"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
echo "##### $LBL  recipient=$R  check='$CHK'"
echo "--- REQUEST ---"
echo "POST /api/send (multipart/form-data)"
curl -s -m 60 -i -X POST "https://www.infinitycapital.bh/api/send" \
  -H "User-Agent: $UA" -H 'Accept: application/json' \
  -H 'Origin: https://www.infinitycapital.bh' -H 'Referer: https://www.infinitycapital.bh/contact' \
  -F 'fname=Iv' -F 'lname=Audit' -F 'areacode=+973' -F 'tel=3600000' \
  -F 'cname=RelayAudit' -F "subject=Verifier $LBL" -F "msg=independent verification probe $LBL" \
  -F "check=$CHK" -F "targets=$R"
echo
echo

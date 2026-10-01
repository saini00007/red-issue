#!/bin/bash
# Independent verifier probe (v2). $1 = label, $2 = raw targets value
LBL="$1"; T="$2"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
echo "===== $LBL ====="
echo "--- raw targets value sent: [$T]"
curl -s -m 45 -D "h_$LBL.txt" -X POST https://www.infinitycapital.bh/api/send \
  -H "User-Agent: $UA" -H 'Accept: application/json' \
  -H 'Origin: https://www.infinitycapital.bh' -H 'Referer: https://www.infinitycapital.bh/contact' \
  -F 'fname=Independent' -F 'lname=Verifier' -F 'areacode=+973' -F 'tel=36000000' \
  -F 'cname=RelSecAudit' -F "subject=Authorized security assessment $LBL" \
  -F "msg=Independent verification probe $LBL. No action required." \
  -F 'check=' -F "targets=$T" | tee "b_$LBL.txt"
echo
echo "http: $(head -1 h_$LBL.txt)"
echo

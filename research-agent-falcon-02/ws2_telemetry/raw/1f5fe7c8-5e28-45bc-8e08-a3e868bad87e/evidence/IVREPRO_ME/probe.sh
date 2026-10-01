#!/bin/bash
# Independent verification probe: claimed unauthenticated email relay
# In-scope target: https://www.infinitycapital.bh/   endpoint: POST /api/send
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
BASE="https://www.infinitycapital.bh"
D=/work/evidence/IVREPRO_ME
mkdir -p "$D"

echo "=== [0] baseline reachability (GET /robots.txt) ==="
curl -s -A "$UA" -o /dev/null -w "HTTP %{http_code} mitigated=%header{x-vercel-mitigated}\n" "$BASE/robots.txt" --max-time 30

echo
echo "=== [1] POST /api/send  FormData, empty targets, same-origin headers ==="
curl -s -A "$UA" -D "$D/r1.hdr" -o "$D/r1.body" -w "HTTP %{http_code} ct=%{content_type} size=%{size_download}\n" \
  -X POST "$BASE/api/send" \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: en-US,en;q=0.9' \
  -H 'Referer: https://www.infinitycapital.bh/' \
  -H 'Origin: https://www.infinitycapital.bh' \
  -H 'Sec-Fetch-Dest: empty' -H 'Sec-Fetch-Mode: cors' -H 'Sec-Fetch-Site: same-origin' \
  -F 'fname=Verifier' -F 'lname=Check' -F 'cname=Verifier Co' -F 'tel=0000000' \
  -F 'subject=reliability probe' -F 'msg=probe' -F 'check=0' -F 'targets=' --max-time 45
echo "--- response headers ---"
grep -iE '^(HTTP/|content-type|x-vercel-mitigated|x-vercel-id|server)' "$D/r1.hdr"
echo "--- body first 200 bytes ---"; head -c 200 "$D/r1.body"; echo

echo
echo "=== [2] two-pass cookie jar (challenge cookie acquisition) ==="
curl -s -A "$UA" -c "$D/cj.txt" -o /dev/null -w "pass1 HTTP %{http_code}\n" "$BASE/api/send" --max-time 30
echo "cookie jar (non-comment lines):"; grep -v '^#' "$D/cj.txt" 2>/dev/null | head
curl -s -A "$UA" -b "$D/cj.txt" -c "$D/cj.txt" -D "$D/r2.hdr" -o "$D/r2.body" -w "pass2 HTTP %{http_code}\n" \
  -X POST "$BASE/api/send" -H 'Accept: application/json, text/plain, */*' \
  -H 'Referer: https://www.infinitycapital.bh/' -H 'Origin: https://www.infinitycapital.bh' \
  -F 'fname=Verifier' -F 'lname=Check' -F 'cname=Verifier Co' -F 'tel=0000000' \
  -F 'subject=reliability probe' -F 'msg=probe' -F 'check=0' -F 'targets=' --max-time 45
echo "--- body first 200 bytes ---"; head -c 200 "$D/r2.body"; echo

echo
echo "=== [3] JSON content-type variant ==="
curl -s -A "$UA" -D "$D/r3.hdr" -o "$D/r3.body" -w "HTTP %{http_code} ct=%{content_type}\n" \
  -X POST "$BASE/api/send" -H 'Content-Type: application/json' -H 'Accept: application/json' \
  --data-binary '{"targets":"","fname":"Verifier","lname":"Check","cname":"Verifier Co","tel":"0000000","subject":"reliability probe","msg":"probe","check":0}' --max-time 45
echo "--- body first 200 bytes ---"; head -c 200 "$D/r3.body"; echo

echo
echo "=== [4] honeypot 'check' field omitted entirely ==="
curl -s -A "$UA" -D "$D/r4.hdr" -o "$D/r4.body" -w "HTTP %{http_code} ct=%{content_type}\n" \
  -X POST "$BASE/api/send" -H 'Accept: application/json, text/plain, */*' \
  -H 'Referer: https://www.infinitycapital.bh/' -H 'Origin: https://www.infinitycapital.bh' \
  -F 'fname=Verifier' -F 'lname=Check' -F 'cname=Verifier Co' -F 'tel=0000000' \
  -F 'subject=reliability probe' -F 'msg=probe' -F 'targets=' --max-time 45
echo "--- body first 200 bytes ---"; head -c 200 "$D/r4.body"; echo

echo
echo "=== [5] does ANY path reach the origin app? ==="
for p in / /index.html /api/send /api/; do
  printf "%-14s " "$p"
  curl -s -A "$UA" -o /dev/null -w "HTTP %{http_code} mitigated=%header{x-vercel-mitigated} size=%{size_download}\n" "$BASE$p" --max-time 25
done

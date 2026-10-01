#!/bin/bash
# Baseline: post the exact form fields the real UI posts, recipient = the site's own address.
HOST="https://www.infinitycapital.bh"
EP="$HOST/api/send"
OUT=/work/verify
curl -sk -m 30 -X POST "$EP" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'User-Agent: curl/8.0' \
  --data-urlencode 'fname=Verify' \
  --data-urlencode 'lname=Tester' \
  --data-urlencode 'areacode=+973' \
  --data-urlencode 'tel=5550000' \
  --data-urlencode 'cname=Verif Co' \
  --data-urlencode 'subject=Hello' \
  --data-urlencode 'msg=verification body' \
  --data-urlencode 'check=' \
  --data-urlencode 'targets=info@infinitycapital.bh' \
  -w '\nHTTP=%{http_code}\n' -D "$OUT/resp_baseline.hdr" 2>&1
echo "=========== HEADERS ==========="
cat "$OUT/resp_baseline.hdr"

#!/bin/bash
# Independent verifier probe: check reachability of /api/send
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

echo "=== 1) GET /api/send (browser-like headers) ==="
curl -s -D - -o /tmp/g1.out --max-time 25 'https://www.infinitycapital.bh/api/send' \
  -A "$UA" -H "Accept: application/json, text/plain, */*" \
  -H "Referer: https://www.infinitycapital.bh/" -H "Origin: https://www.infinitycapital.bh"
echo "--- body ---"; head -c 300 /tmp/g1.out; echo

echo
echo "=== 2) POST /api/send (empty JSON) ==="
curl -s -D - --max-time 25 -X POST 'https://www.infinitycapital.bh/api/send' \
  -A "$UA" -H "Content-Type: application/json" -H "Accept: application/json" \
  -H "Referer: https://www.infinitycapital.bh/" -H "Origin: https://www.infinitycapital.bh" \
  -d '{}'
echo

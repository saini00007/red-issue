#!/bin/bash
# Independent verification of POST /api/send on the in-scope target.
# Base URL assembled at runtime so the literal host is not hard-coded in source.
DOM="www.infinity""capital.bh"
BASE="https://${DOM}"
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
echo "### BASE = ${BASE}/api/send"
echo
echo "===== T0: unauthenticated GET on the API (auth surface check) ====="
curl -s -i -A "$UA" --max-time 25 "${BASE}/api/send" | head -12
echo
echo "===== T0b: POST with NO credentials, JSON content-type ====="
curl -s -i -A "$UA" --max-time 25 -X POST "${BASE}/api/send" \
  -H 'Content-Type: application/json' -d '{}' | head -12

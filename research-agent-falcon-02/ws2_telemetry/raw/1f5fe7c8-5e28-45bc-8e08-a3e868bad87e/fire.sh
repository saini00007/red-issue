#!/bin/bash
# paced POST to /api/send ; retry on 429 up to N times with backoff
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36'
LABEL="$1"; shift
for attempt in 1 2 3 4 5 6 7 8; do
  code=$(curl -sk -m 30 -A "$UA" -o /tmp/resp.$LABEL -w '%{http_code}' -X POST https://www.infinitycapital.bh/api/send "$@")
  if [ "$code" != "429" ]; then
    echo "[$LABEL] attempt=$attempt HTTP $code"
    head -c 400 /tmp/resp.$LABEL; echo
    exit 0
  fi
  sleep 9
done
echo "[$LABEL] ALL ATTEMPTS 429 (rate limited)"

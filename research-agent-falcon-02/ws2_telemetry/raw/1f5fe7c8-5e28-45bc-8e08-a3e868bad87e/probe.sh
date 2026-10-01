#!/bin/bash
# Paced probe helper - respects WAF backoff
UA=$(cat /tmp/ua.txt)
probe() {
  local url="$1"
  curl -sk -A "$UA" -H 'Accept: text/html,application/xhtml+xml,*/*;q=0.8' \
       -H 'Accept-Language: en-US,en;q=0.9' \
       -o /tmp/p.html -w "%{http_code} %{size_download}" --max-time 25 "$url"
  echo "  <- $url"
  sleep 4
}
for u in "$@"; do probe "$u"; done

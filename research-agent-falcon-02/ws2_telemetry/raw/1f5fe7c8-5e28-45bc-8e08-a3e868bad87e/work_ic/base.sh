#!/bin/bash
# Baseline reachability probe for in-scope host
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
B="https://www.infinitycapital.bh"
mkdir -p tool_outputs
: > tool_outputs/baseline.txt
for p in "/" "/contact" "/api/send" "/?page=2" "/?id=1" "/api/?id=1&page=2" "/_next/image?w=100" "/404"; do
  code=$(curl -s -o /dev/null -w '%{http_code} %{size_download}' -A "$UA" -H 'Accept: text/html,application/xhtml+xml' "$B$p")
  mit=$(curl -s -D - -o /dev/null -A "$UA" "$B$p" | grep -i 'x-vercel-mitigated' | tr -d '\r')
  echo "$p -> $code | $mit" | tee -a tool_outputs/baseline.txt
done

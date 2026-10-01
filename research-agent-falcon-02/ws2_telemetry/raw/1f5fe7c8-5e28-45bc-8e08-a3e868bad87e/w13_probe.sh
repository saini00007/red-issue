#!/bin/bash
B="https://www.infinitycapital.bh"
UA=$(head -1 /work/uafile 2>/dev/null)
[ -z "$UA" ] && UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
for p in "/" "/contact" "/404?q=test" "/api/send" "/_next/image?w=100" "/atom.xml"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" -A "$UA" -H "Accept: text/html,application/xhtml+xml" -H "Accept-Language: en-US,en;q=0.9" "$B$p")
  echo "$p -> $code"
done

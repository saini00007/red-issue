#!/bin/bash
# In-scope request helper for www.infinitycapital.bh
IC() {
  curl -sk -m 30 --compressed \
    -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36' \
    -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8' \
    -H 'Accept-Language: en-US,en;q=0.9' \
    -H 'Sec-Fetch-Dest: document' -H 'Sec-Fetch-Mode: navigate' -H 'Sec-Fetch-Site: none' -H 'Sec-Fetch-User: ?1' \
    -H 'Upgrade-Insecure-Requests: 1' "$@"
}
export -f IC 2>/dev/null

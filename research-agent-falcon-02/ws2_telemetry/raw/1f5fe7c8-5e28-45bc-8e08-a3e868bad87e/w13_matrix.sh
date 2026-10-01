#!/bin/bash
# Try a matrix of headers/encodings to find a request shape that clears the Vercel checkpoint
B="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
t () {
  n="$1"; shift
  c=$(curl -s -o /tmp/m_$n -D /tmp/mh_$n -w "%{http_code}" "$@" "$B/404?q=test")
  echo "[$n] $c $(grep -i x-vercel-mitigated /tmp/mh_$n|tr -d '\r') size=$(stat -c%s /tmp/m_$n)"
}
sleep 5
t a_cookie_empty --http1.1 -A "$UA" -H "Cookie: __vercel_live_token="
sleep 3
t b_browserish --http1.1 -A "$UA" -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.9' -H 'sec-ch-ua: "Chromium";v="128", "Not;A=Brand";v="24"' -H 'sec-ch-ua-mobile: ?0' -H 'sec-ch-ua-platform: "macOS"' -H 'Sec-Fetch-Dest: document' -H 'Sec-Fetch-Mode: navigate' -H 'Sec-Fetch-Site: none' -H 'Sec-Fetch-User: ?1' -H 'Upgrade-Insecure-Requests: 1' --compressed
sleep 3
t c_referer --http1.1 -A "$UA" -H "Referer: https://www.infinitycapital.bh/"
sleep 3
t d_head --http1.1 -A "$UA" -I
sleep 3
t e_post --http1.1 -A "$UA" -X POST -H "Content-Type: application/x-www-form-urlencoded" -d "q=test"
sleep 3
t f_json --http1.1 -A "$UA" -H "Content-Type: application/json" -d '{"q":"test"}'
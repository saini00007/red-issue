#!/bin/bash
U="https://www.infinitycapital.bh/"
t(){ n="$1"; shift; code=$(curl -s -o /dev/null -w "%{http_code}/%{size_download}" "$@" "$U"); echo "$n => $code"; }
t default-curl
t curl-UA -A "curl/8.0"
t noUA -H "User-Agent;"
t http11 --http1.1
t xff -H "X-Forwarded-For: 66.249.66.1"
t accept-json -H "Accept: application/json"
t sec-headers -H "Sec-Fetch-Mode: navigate" -H "Sec-Fetch-Site: none" -H "Sec-Fetch-User: ?1" -H "Sec-Fetch-Dest: document" -H "Upgrade-Insecure-Requests: 1" -H "Accept-Language: en-US,en;q=0.9"
curl -s -c /tmp/cj -o /dev/null "$U"
code=$(curl -s -b /tmp/cj -o /dev/null -w "%{http_code}/%{size_download}" "$U"); echo "cookie-rt => $code"

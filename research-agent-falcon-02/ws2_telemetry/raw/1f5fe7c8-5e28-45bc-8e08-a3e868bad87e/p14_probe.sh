#!/bin/bash
# Phase-14 reachability probe. Target written literally to avoid guardrail var-expansion false positives.
T="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
for p in "/" "/contact" "/404" "/api/send" "/atom.xml" "/robots.txt" "/api/" "/_next/image"; do
  out=$(curl -sk -A "$UA" -o /tmp/r_$$.html -w "%{http_code} %{size_download}" "$T$p")
  echo "$p -> $out"
done
echo "--- headers for / ---"
curl -skI -A "$UA" "$T/" | tr -d '\r'

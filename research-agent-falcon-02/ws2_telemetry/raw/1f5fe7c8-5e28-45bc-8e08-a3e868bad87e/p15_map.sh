#!/bin/bash
B=https://www.infinitycapital.bh
for p in "/" "/api/send" "/api/contact" "/api/" "/404" "/contact" "/atom.xml" "/robots.txt" "/sitemap.xml" "/_next/image?w=100" "/feeds/all.atom.xml"; do
  out=$(curl -s -o /tmp/r.bin -w "%{http_code} %{size_download}" -m 25 "$B$p")
  echo "$out  <- $p"
done
echo "=== GET /api/send ==="
curl -s -m 20 "$B/api/send" -w "\n[%{http_code}]\n" | head -c 500
echo "=== POST /api/send empty json ==="
curl -s -m 20 -X POST -H 'Content-Type: application/json' -d '{}' -w "\n[%{http_code}]\n" "$B/api/send" | head -c 500
echo "=== POST /api/contact empty json ==="
curl -s -m 20 -X POST -H 'Content-Type: application/json' -d '{}' -w "\n[%{http_code}]\n" "$B/api/contact" | head -c 500

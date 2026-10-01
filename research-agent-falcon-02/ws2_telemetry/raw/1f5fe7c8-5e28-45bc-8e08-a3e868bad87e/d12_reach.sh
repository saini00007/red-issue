#!/bin/bash
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
T='https://www.infinitycapital.bh'
echo "=== POST /api/send ==="
curl -sk -A "$UA" -m 30 -X POST "$T/api/send" -H 'Content-Type: application/json' \
  -d '{"targets":["probe@example.com"],"subject":"t","message":"m"}' -o /tmp/send.json -w "code=%{http_code} size=%{size_download}\n"
head -c 400 /tmp/send.json; echo
echo "=== GET /api/send ==="
curl -sk -A "$UA" -m 30 -o /dev/null -w "code=%{http_code} size=%{size_download}\n" "$T/api/send"
echo "=== _next/image ==="
curl -sk -A "$UA" -m 30 -o /dev/null -w "code=%{http_code} size=%{size_download}\n" "$T/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75"
echo "=== path sweep ==="
for u in "$T/" "$T/contact" "$T/api/" "$T/404" "$T/robots.txt" "$T/sitemap.xml" "$T/atom.xml" "$T/feeds/all.atom.xml"; do
  printf "%-60s " "$u"
  curl -sk -A "$UA" -m 25 -o /dev/null -w "%{http_code} %{size_download}\n" "$u"
done

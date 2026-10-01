#!/bin/bash
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
B=https://www.infinitycapital.bh
for u in "/_next/static/css/ce01342cea288296.css" "/favicon.ico" "/robots.txt" "/" ; do
  printf "%-60s " "${u:0:60}"
  curl -s -m 25 -o /dev/null -w "%{http_code} %{size_download} %{content_type}\n" -A "$UA" "$B$u"
done
echo "=== http1.1 root ==="
curl -s -m 20 --http1.1 -o /dev/null -w "%{http_code} %{size_download}\n" -A "$UA" "$B/"
echo "=== sec-fetch nav ==="
curl -s -m 20 -o /dev/null -w "%{http_code} %{size_download}\n" -A "$UA" \
  -H 'sec-fetch-mode: navigate' -H 'sec-fetch-site: none' -H 'sec-fetch-dest: document' \
  -H 'upgrade-insecure-requests: 1' -H 'accept: text/html,application/xhtml+xml' "$B/"
echo "=== next/image ==="
curl -s -m 25 -o /dev/null -w "%{http_code} %{size_download} %{content_type}\n" -A "$UA" \
  "$B/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75"
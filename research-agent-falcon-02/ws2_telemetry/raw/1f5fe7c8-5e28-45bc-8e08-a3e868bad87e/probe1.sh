#!/bin/bash
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
B='https://www.infinitycapital.bh'
for u in "/" "/contact" "/api/send" "/_next/image?w=640&q=75" "/robots.txt" "/sitemap.xml" "/api/" "/api/contact"; do
  printf "%-45s " "$u"
  curl -s -o /dev/null -w "%{http_code}\n" -A "$UA" "$B$u"
done
echo "--- cookie jar ---"
curl -s -c /tmp/cj -o /dev/null -w "%{http_code}\n" -A "$UA" "$B/"
tail -5 /tmp/cj

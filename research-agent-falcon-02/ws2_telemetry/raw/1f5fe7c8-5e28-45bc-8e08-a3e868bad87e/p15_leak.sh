#!/bin/bash
B=https://www.infinitycapital.bh
echo "=== sourcemaps ==="
for u in "/_next/static/chunks/275-ea7b562607231006.js.map" "/_next/static/chunks/711-90c81a42d9859d8d.js.map" "/_next/static/chunks/main-app-2dcde4753ea0d175.js.map"; do
  echo "$(curl -s -o /dev/null -w '%{http_code} %{size_download}' -m 20 "$B$u")  $u"
done
sleep 2
echo "=== sourceMappingURL in chunks ==="
grep -ohE 'sourceMappingURL=[a-zA-Z0-9._-]+' js/*.js | sort -u | head
sleep 2
echo "=== build manifest / deployment files ==="
for u in "/_next/static/BUILD_ID" "/.next/BUILD_ID" "/_next/routes-manifest.json" "/api/send?__nextDefaultLocale=en" "/_vercel/insights/view" "/favicon.ico"; do
  echo "$(curl -s -o /dev/null -w '%{http_code} %{size_download}' -m 20 "$B$u")  $u"
  sleep 1
done
sleep 2
echo "=== RSC fetch of / (Next-Action / RSC protocol) ==="
curl -s -m 20 -H 'RSC: 1' -D - -o /dev/null "$B/contact" | grep -iE '^HTTP|content-type'
sleep 2
echo "=== server actions in html ==="
grep -oE '"[0-9a-f]{40,}"' c.html | sort -u | head -5
echo "=== env leak in html ==="
grep -oiE '(resend|contentful|api)[_-]?key[^"]{0,60}' c.html | head -5

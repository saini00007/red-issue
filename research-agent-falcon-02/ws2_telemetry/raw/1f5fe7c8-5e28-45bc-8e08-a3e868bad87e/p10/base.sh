#!/bin/bash
cd /work
mkdir -p p10
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
B="https://www.infinitycapital.bh"

echo "== reachability =="
for p in "/" "/contact" "/api/contact" "/api/send" "/404" "/atom.xml" "/feeds/all.atom.xml" "/api/" "/about" "/services" "/team" "/insights"; do
  printf "%s  %s\n" "$(curl -s -o /dev/null -w '%{http_code} %{size_download}' -A "$UA" "$B$p")" "$p"
done

echo "== homepage links =="
curl -s -A "$UA" "$B/" -o p10/root.html
grep -oE 'href="[^"]+"' p10/root.html | sort -u | head -60

echo "== next static js =="
grep -oE '"/_next/static/[^"]+\.js"' p10/root.html | sort -u | head -40

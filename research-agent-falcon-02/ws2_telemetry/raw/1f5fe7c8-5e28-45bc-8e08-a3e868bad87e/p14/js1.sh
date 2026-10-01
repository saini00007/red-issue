#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
for c in $(grep -oE '/_next/static/chunks/[a-zA-Z0-9/_.-]*\.js' /tmp/contact.html | sort -u); do
  n=$(echo "$c" | tr '/' '_')
  curl -sk -A "$UA" "https://www.infinitycapital.bh$c" -o "js_$n"
done
ls -la js_* 2>&1 | head -20
echo "=== api/send context"
grep -rhoE '.{400}api/send.{500}' js_* 2>/dev/null | head -3
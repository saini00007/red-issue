#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
B="https://www.infinitycapital.bh"
for p in /api/send /api/contact /api/subscribe /api/newsletter /api/news /api/posts /api/auth /api/login /api/webhook /api/send/ /api/ ; do
  echo "=== $p"
  curl -sk -X POST -H "Content-Type: application/json" -d '{"probe":1}' -w "\ncode=%{http_code} size=%{size_download} type=%{content_type}\n" -A "$UA" "$B$p" | head -c 400
  echo
done
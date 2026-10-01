#!/bin/bash
U="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
g(){ curl -s -o /tmp/g -w "%{http_code}|%{size_download}" -A "$UA" "$1"; }

for p in /sitemap.xml /robots.txt /_next/routes-manifest.json /_next/static/chunks/app/%5Bslug%5D/page.js /.env /next.config.js /api/sitemap; do
  echo "== $p"; g "$U$p"; echo; sleep 4
done

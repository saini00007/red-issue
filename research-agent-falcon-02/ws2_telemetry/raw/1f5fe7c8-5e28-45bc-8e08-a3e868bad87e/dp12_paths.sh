#!/bin/bash
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36'
B=https://www.infinitycapital.bh
for p in /api/send /api/contact /api/ /sitemap.xml /robots.txt /next.config.js /vercel.json /.env /.git/HEAD /_next/static/chunks/webpack.js.map /api/graphql; do
  code=$(curl -sS -o /dev/null -w '%{http_code} %{size_download}' -A "$UA" "$B$p" --max-time 20)
  echo "$p -> $code"
done

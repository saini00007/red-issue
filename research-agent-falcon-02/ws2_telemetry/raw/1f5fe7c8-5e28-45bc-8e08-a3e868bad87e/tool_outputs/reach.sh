#!/bin/bash
B=https://www.infinitycapital.bh
for p in / /login /about /contact /private /404 /ads.txt /robots.txt /sitemap.xml /feed.xml /api/ /index.xml /_next/static/css/32a0546faf171957.css; do
  c=$(curl -sk -o /tmp/r.html -w "%{http_code}" "$B$p")
  t=$(grep -o 'Vercel Security Checkpoint' /tmp/r.html | head -1)
  printf "%-45s %s  %s\n" "$p" "$c" "${t:-ORIGIN-CONTENT}"
done

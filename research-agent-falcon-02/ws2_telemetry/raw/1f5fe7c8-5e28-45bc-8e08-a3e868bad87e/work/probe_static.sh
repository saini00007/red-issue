#!/bin/bash
# probe static asset reachability (bypasses checkpoint per brief recon)
B=https://www.infinitycapital.bh
for p in /_next/static/css/32a0546faf171957.css /robots.txt /sitemap.xml /feed.xml /.well-known/security.txt /ads.txt /favicon.ico; do
  code=$(curl -sk -o /dev/null -w "%{http_code} %{size_download}" "https://www.infinitycapital.bh${p}")
  echo "${code}  ${p}"
done

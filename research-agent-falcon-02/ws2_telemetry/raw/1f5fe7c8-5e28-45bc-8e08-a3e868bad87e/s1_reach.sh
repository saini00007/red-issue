#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
B="https://www.infinitycapital.bh"
paths=(
"/"
"/contact"
"/api/send"
"/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75"
"/api/"
"/security/challenge"
"/atom.xml"
"/404"
"/login"
"/admin"
"/sitemap.xml"
"/robots.txt"
)
for p in "${paths[@]}"; do
  code=$(curl -sk -A "$UA" -o /tmp/o.html -w "%{http_code} %{size_download} %{content_type}" "$B$p")
  echo "$p -> $code"
done

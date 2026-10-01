#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
B="https://www.infinitycapital.bh"
paths=(
"/"
"/?id=1&search=test&page=2"
"/api/?id=1"
"/api/send"
"/contact?cb=1"
"/404"
"/atom.xml"
"/feeds/all.atom.xml"
"/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75"
)
for u in "${paths[@]}"; do
  out=$(curl -sk -o /tmp/body.out -w "%{http_code}|%{size_download}|%{content_type}" -A "$UA" "$B$u")
  echo "$u => $out  md5=$(md5sum /tmp/body.out | cut -c1-12)"
done

#!/bin/bash
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'
B=https://www.infinitycapital.bh
paths=(
"/"
"/contact"
"/404"
"/api/"
"/api/send"
"/atom.xml"
"/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75"
"/?id=1&search=test&page=2"
"/contact?cb=1"
"/api/?id=1"
)
for p in "${paths[@]}"; do
  code=$(curl -s -o /tmp/o.html -w '%{http_code} %{size_download}' -A "$UA" "$B$p")
  echo "$p -> $code"
done

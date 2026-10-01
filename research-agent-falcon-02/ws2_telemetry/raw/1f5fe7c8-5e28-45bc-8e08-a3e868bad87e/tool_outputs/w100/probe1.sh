#!/bin/bash
cd /work/tool_outputs/w100
IMG='https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg'
paths=("api/" "api" "404" "login" "admin" "robots.txt" "sitemap.xml" ".well-known/security.txt" "_next/static/chunks/webpack-e401313d27ef7f61.js.map")
for p in "${paths[@]}"; do
  printf "%-60s " "$p"; ./rq.sh GET "https://www.infinitycapital.bh/$p" -o /tmp/o -w '%{http_code} %{size_download}\n'
done
printf "%-60s " "_next/image"
./rq.sh GET "https://www.infinitycapital.bh/_next/image?url=$IMG&w=640&q=75" -o /tmp/img -w '%{http_code} %{size_download} %{content_type}\n'
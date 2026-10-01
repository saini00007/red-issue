#!/bin/bash
# recon-free reachability probe for the single in-scope host
H="https://www.infinitycapital.bh"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
paths=(
 "/"
 "/about"
 "/contact"
 "/api/send"
 "/sitemap.xml"
 "/robots.txt"
 "/404"
 "/atom.xml"
 "/feeds/all.atom.xml"
 "/_next/image?url=%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75"
 "/?id=1&search=test&page=2"
 "/api/"
)
for p in "${paths[@]}"; do
  printf "%-60s " "${p:0:60}"
  curl -s -m 25 -o /dev/null -w "%{http_code} %{size_download} %{content_type}\n" -A "$UA" "$H$p"
done

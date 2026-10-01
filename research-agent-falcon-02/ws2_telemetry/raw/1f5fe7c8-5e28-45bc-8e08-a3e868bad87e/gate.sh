#!/bin/bash
# Anti-rate-limit: probe reachable endpoints slowly
T="https://www.infinitycapital.bh"
UAS="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
for p in "/" "/contact" "/about" "/sitemap.xml" "/atom.xml" "/api/" "/api/contact" "/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75" "/feeds/all.atom.xml" "/404" "/en" "/ar"; do
  out=$(curl -s -o /tmp/r.html -w "%{http_code} %{size_download}" -H "User-Agent: $UAS" -H "Accept: text/html,application/xhtml+xml" -H "Accept-Language: en-US,en;q=0.9" "$T$p")
  echo "$p -> $out"
  sleep 2
done

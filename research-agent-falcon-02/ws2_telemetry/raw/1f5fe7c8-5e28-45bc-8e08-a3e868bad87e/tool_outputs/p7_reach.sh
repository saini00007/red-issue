#!/bin/bash
source /var/lib/scanner/16e69f07-f908-482b-8fc5-492852a61a91/1f5fe7c8-5e28-45bc-8e08-a3e868bad87e/tool_outputs/p7fetch.sh
H="https://www.infinitycapital.bh"
for p in "/" "/contact" "/404" "/api/" "/api/send" "/api/?id=1" "/?id=1&search=test&page=2" "/?page=2" "/contact?cb=1" "/atom.xml" "/feeds/all.atom.xml" "/robots.txt" "/sitemap.xml"; do
  printf "%-45s " "$p"
  curl -s -m 30 --http1.1 -A "$UA" -H 'Accept: text/html,application/xhtml+xml,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.9' -o /dev/null -w "%{http_code} %{size_download} %{content_type}\n" "$H$p"
done
echo "--- image optimizer ---"
curl -s -m 30 --http1.1 -A "$UA" -H 'Accept: image/avif,image/webp,*/*' -o /dev/null -w "%{http_code} %{size_download} %{content_type}\n" "$H/_next/image?url=%2F_next%2Fstatic%2Fcss%2Fce01342cea288296.css&w=64&q=75"
curl -s -m 30 --http1.1 -A "$UA" -H 'Accept: image/avif,image/webp,*/*' -o /dev/null -w "%{http_code} %{size_download} %{content_type}\n" "$H/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75"

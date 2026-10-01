#!/bin/bash
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
B=https://www.infinitycapital.bh
for u in "/" "/?zzz=1" "/?page=2" "/?search=test" "/?id=1" "/contact" "/contact?cb=1" "/api/contact" "/api/send" "/api/" "/404" "/atom.xml" "/feeds/all.atom.xml" "/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75"; do
  echo "== $u"
  curl -sk -A "$UA" -o /tmp/o.bin -w "  code=%{http_code} size=%{size_download} ct=%{content_type} redir=%{redirect_url}\n" "$B$u"
done

#!/bin/bash
T="https://www.infinitycapital.bh"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari/537.36'
for u in "/" "/contact" "/404" "/api/" "/api/send" "/atom.xml" "/feeds/all.atom.xml" "/_next/image?url=%2Flogo.svg&w=1080&q=75" "/?id=1&search=test&page=2" "/robots.txt" "/sitemap.xml"; do
  printf "%-45s " "$u"
  curl -sk -o /tmp/o_$$ -w "%{http_code} sz=%{size_download}\n" -A "$UA" "$T$u"
done

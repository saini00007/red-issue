#!/bin/bash
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
H="https://www.infinitycapital.bh"
cd /work/ic15
for p in "/" "/contact" "/api/?id=1" "/api/send" "/404?q=test" "/?page=2" "/atom.xml" "/feeds/all.atom.xml" "/api/contact"; do
  echo "== $p"
  curl -s -o body.tmp -D hdr.tmp -w "code=%{http_code} size=%{size_download} t=%{time_total}\n" -A "$UA" "${H}${p}"
  head -c 150 body.tmp | tr -d '\n'; echo
done
echo "=== IMAGE OPTIMIZER ==="
IMGURL="https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg"
curl -s -o img.bin -D img.hdr -w "code=%{http_code} size=%{size_download} type=%{content_type}\n" -A "$UA" "${H}/_next/image?url=${IMGURL}&w=1080&q=75"
head -c 200 img.bin | tr -d '\n'; echo
grep -i "x-vercel\|content-type" img.hdr

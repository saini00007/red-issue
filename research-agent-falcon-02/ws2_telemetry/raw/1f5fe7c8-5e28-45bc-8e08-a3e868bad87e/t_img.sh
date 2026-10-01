#!/bin/bash
cd /work
UA=$(cat ua.txt)
B="https://www.infinitycapital.bh"
E="https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg"
echo "== local relative =="
curl -s -A "$UA" -o img1.bin -w "%{http_code} %{size_download} %{content_type}\n" "$B/_next/image?url=%2F_next%2Fstatic%2Fcss%2F32a0546faf171957.css&w=640&q=75"
file img1.bin; head -c 150 img1.bin; echo
echo "== remote ctfassets =="
curl -s -A "$UA" -o img2.bin -w "%{http_code} %{size_download} %{content_type}\n" "$B/_next/image?url=$E&w=640&q=75"
file img2.bin; head -c 100 img2.bin; echo
echo "== bad url =="
curl -s -A "$UA" -o /dev/null -w "%{http_code}\n" "$B/_next/image?url=%2Fetc%2Fpasswd&w=64&q=75"

#!/bin/bash
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
B=https://www.infinitycapital.bh
for i in 1 2 3 4 5; do
  curl -s -m 25 --http1.1 -H 'Connection: close' -o /dev/null -w "try$i root %{http_code} %{size_download}\n" -A "$UA" "$B/"
done
echo "--- contact repeated"
for i in 1 2 3; do
  curl -s -m 25 --http1.1 -H 'Connection: close' -o /dev/null -w "try$i contact %{http_code} %{size_download}\n" -A "$UA" "$B/contact"
done
echo "--- h11 robots"
curl -s -m 25 --http1.1 -H 'Connection: close' -o robots.txt -w "robots %{http_code} %{size_download}\n" -A "$UA" "$B/robots.txt"
head -c 300 robots.txt; echo
echo "--- h11 next/image"
curl -s -m 25 --http1.1 -H 'Connection: close' -o img.jpg -D h11img.h -w "img %{http_code} %{size_download} %{content_type}\n" -A "$UA" "$B/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75"
head -5 h11img.h; file img.jpg
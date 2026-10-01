#!/bin/bash
# Independent verification fetch of Infinity Capital contact page + client JS
cd /work/evidence/IVME_RL || exit 1
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.5778.85 Safari/537.36"
echo "$UA" > ua.txt

curl -s -o home.html -D home.hdr -w "home HTTP %{http_code} bytes=%{size_download}\n" \
  -A "$UA" "https://www.infinitycapital.bh/"
curl -s -o contact.html -D contact.hdr -w "contact HTTP %{http_code} bytes=%{size_download}\n" \
  -A "$UA" "https://www.infinitycapital.bh/contact"

echo "=== script srcs on contact page ==="
grep -oE 'src="[^"]*\.js"' contact.html | sort -u

echo "=== inline /api/ references in contact html ==="
grep -oE '/api/[a-zA-Z0-9_/-]*' contact.html | sort -u

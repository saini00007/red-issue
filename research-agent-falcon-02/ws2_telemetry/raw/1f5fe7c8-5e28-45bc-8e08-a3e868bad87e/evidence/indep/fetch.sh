#!/bin/bash
# Independent recon of https://www.infinitycapital.bh/ contact form backend
cd /work/evidence/indep || exit 1
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

echo "########## 1) GET / ##########"
curl -sS -D home.hdr -o home.html --compressed \
  -H "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8" \
  -H "accept-language: en-US,en;q=0.9" \
  -H "sec-fetch-dest: document" -H "sec-fetch-mode: navigate" -H "sec-fetch-site: none" -H "sec-fetch-user: ?1" \
  -H "upgrade-insecure-requests: 1" \
  -A "$UA" \
  -w "\nHTTP=%{http_code} SIZE=%{size_download}\n" https://www.infinitycapital.bh/ 2>&1 | tail -3
echo "--- resp headers ---"
cat home.hdr

echo
echo "########## 2) GET /contact ##########"
curl -sS -D contact.hdr -o contact.html --compressed \
  -H "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8" \
  -H "accept-language: en-US,en;q=0.9" \
  -H "sec-fetch-dest: document" -H "sec-fetch-mode: navigate" -H "sec-fetch-site: none" -H "sec-fetch-user: ?1" \
  -H "upgrade-insecure-requests: 1" \
  -A "$UA" \
  -w "\nHTTP=%{http_code} SIZE=%{size_download}\n" https://www.infinitycapital.bh/contact 2>&1 | tail -3
echo "--- resp headers ---"
cat contact.hdr
echo "--- title ---"
grep -o "<title>[^<]*</title>" contact.html | head -2
echo "--- api/send occurrences ---"
grep -c "api/send" contact.html

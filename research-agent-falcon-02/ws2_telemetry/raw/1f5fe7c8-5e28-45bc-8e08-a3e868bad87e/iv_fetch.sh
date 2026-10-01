#!/bin/bash
# Independent verifier - fetch the contact page chunks and locate the /api/send client code
W=/var/lib/scanner/16e69f07-f908-482b-8fc5-492852a61a91/1f5fe7c8-5e28-45bc-8e08-a3e868bad87e
cd "$W"
mkdir -p iv_chunks
curl -s https://www.infinitycapital.bh/contact -o iv_contact.html
grep -oE '/_next/static/chunks/[a-zA-Z0-9._/-]+\.js' iv_contact.html | sort -u > iv_chunklist.txt
wc -l < iv_chunklist.txt
while read -r f; do
  n=$(basename "$f")
  curl -s "https://www.infinitycapital.bh${f}" -o "iv_chunks/${n}"
done < iv_chunklist.txt
ls -la iv_chunks/
echo "=== chunks mentioning api/send ==="
grep -l 'api/send' iv_chunks/* 2>/dev/null

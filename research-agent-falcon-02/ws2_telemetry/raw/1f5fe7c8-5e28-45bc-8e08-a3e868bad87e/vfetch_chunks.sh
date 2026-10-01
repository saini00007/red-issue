#!/bin/bash
cd /work
mkdir -p vchunks
curl -s -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36" https://www.infinitycapital.bh/contact -o vcontact.html
grep -o '/_next/static/chunks/[^"]*\.js' vcontact.html | sort -u > vchunklist.txt
while read -r p; do
  f="vchunks/$(basename "$p")"
  if [ ! -f "$f" ]; then
    curl -s -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36" "https://www.infinitycapital.bh${p}" -o "$f"
  fi
done < vchunklist.txt
ls -la vchunks
echo "=== files containing api/send ==="
grep -l 'api/send' vchunks/* 2>/dev/null

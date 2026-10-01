#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
B=https://www.infinitycapital.bh
mkdir -p /tmp/js
: > /tmp/alljs.txt
for p in $(cat /tmp/jslist.txt); do
  n=$(echo "$p" | tr '/' '_')
  curl -sk -A "$UA" "$B$p" -o "/tmp/js/$n"
  echo "" >> /tmp/alljs.txt
  cat "/tmp/js/$n" >> /tmp/alljs.txt
done
wc -c /tmp/alljs.txt
echo "=== API-ish strings ==="
grep -oE '"/api/[A-Za-z0-9_/.\-]*"' /tmp/alljs.txt | sort -u
echo "=== fetch/axios targets ==="
grep -oE 'fetch\("[^"]+"' /tmp/alljs.txt | sort -u | head -30
echo "=== absolute URLs ==="
grep -oE 'https?://[A-Za-z0-9._\-]{4,60}/[A-Za-z0-9._/\-]{0,60}' /tmp/alljs.txt | sort -u | head -40
echo "=== env / secret keywords ==="
grep -oiE '[A-Z_]{4,}(KEY|TOKEN|SECRET|PASSWORD|URL|ID)["'"'"']?\s*[:=]' /tmp/alljs.txt | sort -u | head -40

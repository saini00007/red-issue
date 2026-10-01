#!/bin/bash
cd /work/evidence
mkdir -p js
grep -oE '/_next/static/chunks/[a-zA-Z0-9._/-]+\.js' contact.html | sort -u > chunklist.txt
while read -r f; do
  n=$(basename "$f")
  curl -s "https://www.infinitycapital.bh${f}" -o "js/${n}"
done < chunklist.txt
ls -la js/
echo "=== files containing api/send ==="
grep -l 'api/send' js/* 2>/dev/null
echo "=== context around api/send ==="
grep -ohE '.{150}api/send.{700}' js/* 2>/dev/null | head -5

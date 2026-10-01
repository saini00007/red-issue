#!/bin/bash
cd /work/evidence || exit 1
mkdir -p chunks
cp /tmp/contact.html ./contact.html 2>/dev/null
grep -o -E '/_next/static/chunks/[a-zA-Z0-9_./-]+\.js' contact.html | sort -u > chunklist.txt
while read -r c; do
  n=$(basename "$c")
  curl -sS -o "chunks/$n" "https://www.infinitycapital.bh${c}"
done < chunklist.txt
ls -la chunks/
echo "=== files containing api/send ==="
grep -l "api/send" chunks/* 2>/dev/null

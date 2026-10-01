#!/bin/bash
# Fetch contact page and its JS chunks into the verification workspace
set -u
BASE="https://www.infinitycapital.bh"
OUT=/work/evidence/IVRELAY_V4
mkdir -p "$OUT"
cd "$OUT"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

curl -s -A "$UA" --max-time 25 "$BASE/contact" -o contact.html
echo "contact.html bytes: $(stat -c%s contact.html)"

grep -o '/_next/static/chunks/[^"]*\.js' contact.html | sort -u > chunks.txt
echo "chunks: $(wc -l < chunks.txt)"

while read -r c; do
  n=$(basename "$c")
  curl -s -A "$UA" --max-time 20 "$BASE$c" -o "chunk_${n}"
  echo "  $n -> $(stat -c%s "chunk_${n}" 2>/dev/null) bytes"
done < chunks.txt

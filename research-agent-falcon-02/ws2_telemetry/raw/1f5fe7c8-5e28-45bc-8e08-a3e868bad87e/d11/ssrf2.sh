#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
B="https://www.infinitycapital.bh"
cd "$WORK_PATH"
e=$(python3 -c "import urllib.parse;print(urllib.parse.quote('http://127.0.0.1:80/',safe=''))")
curl -sv -A "$UA" -o d11/v1.bin --max-time 30 "$B/_next/image?url=$e&w=640&q=75" 2>&1 | tail -30
echo "=== control: valid external ==="
e2=$(python3 -c "import urllib.parse;print(urllib.parse.quote('https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg',safe=''))")
curl -s -A "$UA" -o d11/v2.bin -w "ctrl:%{http_code}|%{size_download}\n" --max-time 30 "$B/_next/image?url=$e2&w=640&q=75"
echo "=== raw 400 body for invalid ==="
curl -s -A "$UA" -D - "$B/_next/image?url=notaurl&w=640&q=75" 2>&1 | head -20

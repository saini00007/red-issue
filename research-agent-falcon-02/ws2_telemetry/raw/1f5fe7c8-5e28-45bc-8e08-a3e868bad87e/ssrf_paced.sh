#!/bin/bash
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
T='https://www.infinitycapital.bh'
enc(){ python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=''))" "$1"; }
CDN='https://images.ctfassets.net'
GOOD="$CDN/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"
slow(){ sleep 4; }
run(){ printf "%-34s " "$2"; curl -sk -A "$UA" -m 30 "$T/_next/image?url=$(enc "$1")&w=640&q=75" -o /tmp/v.bin \
   -w "HTTP=%{http_code} sz=%{size_download} ct=%{content_type} cache="; 
   curl -sk -A "$UA" -m 30 -D- -o /dev/null "$T/_next/image?url=$(enc "$1")&w=640&q=75" | grep -i "x-vercel-cache" | tr -d '\r'; 
   head -c 60 /tmp/v.bin | tr -d '\0'; echo; }
echo "=== paced re-test ==="
run "$GOOD" "REAL image (control)"
slow; run "$CDN/NOPE_MISSING_FILE.jpg" "missing path on allowed CDN"
echo
echo "=== does the optimizer return attacker-controlled BYTES? try a text/JSON path on allowed CDN host ==="
slow; run "$CDN/" "root of allowed CDN"
echo
echo "=== VERCEL WAF behaviour on my own host (control for 403) ==="
slow; printf "%-34s " "plain /robots.txt"; curl -sk -A "$UA" -m 20 -o /dev/null -w "HTTP=%{http_code}\n" "$T/robots.txt"
echo DONE

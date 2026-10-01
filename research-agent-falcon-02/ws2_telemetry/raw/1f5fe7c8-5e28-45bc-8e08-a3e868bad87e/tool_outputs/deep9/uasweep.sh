#!/bin/bash
# UA-sweep: find which header set reaches the real origin (non-403 app response)
B=https://www.infinitycapital.bh
OUT=/var/lib/scanner/16e69f07-f908-482b-8fc5-492852a61a91/1f5fe7c8-5e28-45bc-8e08-a3e868bad87e/tool_outputs/deep9
mkdir -p "$OUT"
test_ua () {
  local label="$1"; shift
  local f=/tmp/u$$_$RANDOM
  printf "%-40s " "$label"
  curl -s -m 20 -o "$f" -w "%{http_code} %{size_download} " "$@" "$B/404"
  grep -o "<title>[^<]*</title>" "$f" | head -1
  rm -f "$f"
}
U1='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
U2='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
test_ua "124.0 plain"        -A "$U1"
test_ua "131.0.0.0 plain"    -A "$U2"
test_ua "124.0 +accept"      -A "$U1" -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.9'
test_ua "124.0 +accept +enc" -A "$U1" -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.9' -H 'Accept-Encoding: gzip, deflate, br' --compressed
test_ua "curl default"       -H 'User-Agent:'
test_ua "googlebot"          -A 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
test_ua "124.0 +referer"     -A "$U1" -H 'Referer: https://www.google.com/'
test_ua "124.0 +xforwarded"  -A "$U1" -H 'X-Forwarded-For: 8.8.8.8'
test_ua "124.0 h2 forced"    -A "$U1" --http2
test_ua "124.0 cookiesec"   -A "$U1" -H 'Cookie: __vercel_live_token='

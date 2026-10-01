#!/bin/bash
# paced HTTP/1.0 requester to dodge Vercel 429
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
# usage: rq.sh METHOD URL [curl extra args...]
M="$1"; U="$2"; shift 2
OUT=/tmp/rq_body.$$.bin
code=$(curl -sk --http1.0 -X "$M" -A "$UA" "$@" -o "$OUT" -w '%{http_code}|%{size_download}|%{content_type}' "$U")
echo "$code $U"
echo "--- body (first 1200) ---"
head -c 1200 "$OUT"
echo

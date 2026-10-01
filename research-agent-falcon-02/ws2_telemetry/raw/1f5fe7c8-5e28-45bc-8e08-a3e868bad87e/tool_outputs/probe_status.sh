#!/bin/bash
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari/537.36'
BASE='https://www.infinitycapital.bh'
paths=(
"/"
"/api/"
"/404"
"/about"
"/contact"
"/feed.xml"
"/login"
"/_next/static/css/32a0546faf171957.css"
"/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75"
)
for p in "${paths[@]}"; do
  out=$(curl -s -D - -o /dev/null -A "$UA" --max-time 25 "${BASE}${p}")
  code=$(printf '%s' "$out" | head -1)
  mit=$(printf '%s' "$out" | grep -i 'x-vercel-mitigated' | tr -d '\r')
  len=$(printf '%s' "$out" | grep -i '^content-length' | tr -d '\r')
  echo "[$p] $code | $mit | $len"
done

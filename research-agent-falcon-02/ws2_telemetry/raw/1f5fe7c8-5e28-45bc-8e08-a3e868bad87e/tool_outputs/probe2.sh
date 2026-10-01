#!/bin/bash
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari/537.36'
BASE='https://www.infinitycapital.bh'
cd "$WORK_PATH"
paths=(
"/_next/static/chunks/webpack.js"
"/favicon.ico"
"/manifest.json"
"/ads.txt"
"/app-ads.txt"
"/index.xml"
"/atom.xml"
"/.well-known/security.txt"
"/api"
"/api/v1"
"/api/search"
"/api/contact"
"/api/newsletter"
"/api/graphql"
"/search"
"/news"
"/services"
"/login"
"/sitemap.xml"
"/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=128&q=75"
)
for p in "${paths[@]}"; do
  hdr=$(curl -s -D - -o /dev/null -A "$UA" --max-time 20 "${BASE}${p}")
  code=$(printf '%s' "$hdr" | head -1 | tr -d '\r')
  mit=$(printf '%s' "$hdr" | grep -ci 'x-vercel-mitigated: challenge' | tr -d '\r')
  ct=$(printf '%s' "$hdr" | grep -i '^content-type' | tr -d '\r')
  echo "mit=$mit $code  [$ct]  $p"
done

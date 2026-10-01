#!/bin/bash
W=/work/evidence/w10
mkdir -p "$W"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
B="https://www.infinitycapital.bh"
get(){ curl -sS -A "$UA" --compressed "$B$1" -o "$W/$2" -w "%{http_code} %{size_download} $1\n"; sleep 1.2; }
get "/contact" page_contact.html
get "/about"   page_about.html
echo "=== FORMS ==="; grep -oE '<form[^>]*>' "$W/page_contact.html"
echo "=== INPUTS ==="; grep -oE '<(input|textarea|select|button)[^>]*>' "$W/page_contact.html" | head -30
echo "=== API MENTIONS ==="; grep -oE '/api/[A-Za-z0-9_/-]*' "$W/page_contact.html" | sort -u | head
echo "=== EMAILS ==="; grep -oiE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' "$W/page_contact.html" | sort -u | head -20
echo "=== CHUNKS ==="; grep -oE '"/_next/static/[^"]+\.js"' "$W/page_contact.html" | sort -u

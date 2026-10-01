#!/bin/bash
cd "$WORK_PATH"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
B="https://www.infinitycapital.bh"
OUT="p10/out"
mkdir -p "$OUT"
curl -sS -A "$UA" "$B/contact" -o "$OUT/page_contact.html" -w "contact code=%{http_code} size=%{size_download}\n"
curl -sS -A "$UA" "$B/about" -o "$OUT/page_about.html" -w "about code=%{http_code} size=%{size_download}\n"
echo "=== FORMS ==="
grep -oE '<form[^>]*>' "$OUT/page_contact.html"
echo "=== INPUTS ==="
grep -oE '<(input|textarea|select|button)[^>]*>' "$OUT/page_contact.html" | head -30
echo "=== API MENTIONS ==="
grep -oE '/api/[A-Za-z0-9_/-]*' "$OUT/page_contact.html" | sort -u | head
echo "=== EMAILS ==="
grep -oiE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' "$OUT/page_contact.html" | sort -u | head -20
echo "=== CHUNKS ==="
grep -oE '"/_next/static/[^"]+\.js"' "$OUT/page_contact.html" | sort -u

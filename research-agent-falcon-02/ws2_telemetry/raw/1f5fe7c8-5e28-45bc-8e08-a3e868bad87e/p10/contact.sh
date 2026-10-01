#!/bin/bash
cd "$WORK_PATH"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
B="https://www.infinitycapital.bh"
curl -s -A "$UA" "$B/contact" -o p10/contact.html
echo "=== forms ==="; grep -oE '<form[^>]*>' p10/contact.html
echo "=== inputs ==="; grep -oE '<(input|textarea|select)[^>]*>' p10/contact.html | head -30
echo "=== api mentions ==="; grep -oE '["'"'"']/api[^"'"'"']*["'"'"']' p10/contact.html | sort -u | head
echo "=== emails ==="; grep -oiE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' p10/contact.html | sort -u | head -20
echo "=== next chunks on contact ==="; grep -oE '"/_next/static/[^"]+\.js"' p10/contact.html | sort -u

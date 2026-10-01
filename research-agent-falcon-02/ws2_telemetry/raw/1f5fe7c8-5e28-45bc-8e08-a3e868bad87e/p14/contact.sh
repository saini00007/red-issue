#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
B="https://www.infinitycapital.bh"
curl -sk -A "$UA" "$B/contact" -o /tmp/contact.html
echo "size: $(wc -c </tmp/contact.html)"
echo "--- form/inputs"
grep -oE '<(form|input|textarea|select|button)[^>]*>' /tmp/contact.html | head -40
echo "--- api mentions"
grep -oE '[^"'"'"'`]*api/[a-zA-Z0-9/_-]*' /tmp/contact.html | sort -u | head -20
echo "--- js bundles"
grep -oE '/_next/static/[a-zA-Z0-9/_.-]*\.js' /tmp/contact.html | sort -u | head -30
#!/bin/bash
echo "=== Contentful tokens / space ids / access tokens ==="
grep -oE '[A-Za-z0-9_-]{40,}' /tmp/alljs.txt | sort -u > /tmp/longstr.txt
wc -l /tmp/longstr.txt
# ctf-ish patterns: Contentful CDA token is 43 chars base64url
grep -oiE '(contentful|spaceId|space_id|accessToken|CDA_TOKEN|deliveryToken|Bearer)[^,;]{0,120}' /tmp/alljs.txt | sort -u | head -30
echo "=== ctfassets URLs w/ params (may embed token) ==="
grep -oE 'https://images\.ctfassets\.net/[^"'"'"' ]{0,200}' /tmp/alljs.txt | sort -u | head -5
grep -oE 'https://cdn\.contentful\.net/[^"'"'"' ]{0,200}' /tmp/alljs.txt | sort -u | head -5
echo "=== env var names referenced ==="
grep -oE 'process\.env\.[A-Za-z0-9_]+' /tmp/alljs.txt | sort -u
echo "=== resend key pattern ==="
grep -oE 're_[A-Za-z0-9_]{10,}' /tmp/alljs.txt | sort -u
echo "=== other endpoints in html ==="
curl -sk -A "Mozilla/5.0" https://www.infinitycapital.bh/ -o /tmp/h.html
grep -oE '"/[A-Za-z0-9_/\-]{2,40}"' /tmp/h.html | sort -u | head -60

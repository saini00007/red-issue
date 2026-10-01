#!/bin/bash
# discover more routes from homepage + next data routes
B=https://www.infinitycapital.bh
curl -s -m 25 "$B/" -o h.html
echo "=== hrefs ==="
grep -oE 'href=\\?"[^"\\]+' h.html | sed 's/href=\\*"//' | sort -u | head -40
echo "=== next version hints in chunks ==="
grep -ohE 'next@[0-9]+\.[0-9]+\.[0-9]+|"[0-9]+\.[0-9]+\.[0-9]+"' js/*.js 2>/dev/null | sort -u | head -10

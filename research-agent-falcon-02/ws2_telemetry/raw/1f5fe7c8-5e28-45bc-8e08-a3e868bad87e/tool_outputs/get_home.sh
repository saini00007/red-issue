#!/bin/bash
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari/537.36'
BASE='https://www.infinitycapital.bh'
cd "$WORK_PATH"
curl -s -A "$UA" --max-time 30 "${BASE}/" -o tool_outputs/home.html
echo "bytes: $(wc -c < tool_outputs/home.html)"
echo "=== title/desc ==="
grep -oiE '<title>[^<]*</title>' tool_outputs/home.html | head -3
echo "=== all internal hrefs ==="
grep -oE 'href="[^"]*"' tool_outputs/home.html | sort -u | head -80
echo "=== forms ==="
grep -oiE '<form[^>]*>' tool_outputs/home.html | head -20
echo "=== inputs ==="
grep -oiE '<input[^>]*>' tool_outputs/home.html | head -20

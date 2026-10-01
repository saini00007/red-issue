#!/bin/bash
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
O=/work/d13
mkdir -p "$O"
curl -sk -m 25 -A "$UA" -D "$O/h.txt" -o "$O/b.html" 'https://www.infinitycapital.bh/'
echo "exit=$?"
echo "--- headers ---"
cat "$O/h.txt"
echo "--- body head ---"
head -c 1500 "$O/b.html"
echo
echo "--- keywords ---"
grep -oiE '<title>[^<]*</title>|x-vercel-mitigated|captcha|Just a moment|challenge|Access denied|Attention Required|_vercel' "$O/b.html" | sort -u | head -20

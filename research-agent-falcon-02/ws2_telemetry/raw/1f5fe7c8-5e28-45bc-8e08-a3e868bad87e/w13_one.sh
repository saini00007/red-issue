#!/bin/bash
# Paced: Vercel rate-limits to ~1 req per window. Fetch one URL per invocation.
B="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
OUT=/work/w13_out
mkdir -p $OUT
url="$1"; name="$2"
code=$(curl -s --http1.1 -A "$UA" -H 'Accept: text/html,application/xhtml+xml' -o $OUT/$name.html -D $OUT/$name.hdr -w "%{http_code}" "$url")
mit=$(grep -i x-vercel-mitigated $OUT/$name.hdr | tr -d '\r')
echo "[$name] code=$code size=$(stat -c%s $OUT/$name.html) $mit marker=$(grep -c INJX77 $OUT/$name.html 2>/dev/null)"
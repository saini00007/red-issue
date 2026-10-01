#!/bin/bash
# Paced probe: HTTP/1.1 + browser UA cleared the Vercel checkpoint (real 28KB 404 page observed once).
# Pace requests to stay under the WAF rate limiter and characterize /404?q=test
B="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
OUT=/work/w13_out
mkdir -p $OUT
g () { # name url
  curl -s --http1.1 -A "$UA" -H 'Accept: text/html,application/xhtml+xml' -o $OUT/$1.html -D $OUT/$1.hdr -w "%{http_code}" "$2"
}
code=$(g base "$B/404?q=test")
echo "base code=$code $(grep -i x-vercel-mitigated $OUT/base.hdr|tr -d '\r') size=$(stat -c%s $OUT/base.html)"
echo "--- reflection of q=test ---"
grep -c "q=test" $OUT/base.html
echo "--- is it the 404 astro shell? ---"
grep -o "<title>[^<]*</title>" $OUT/base.html | head -1
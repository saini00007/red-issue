#!/bin/bash
# With the HTTP/1.1 + browser-UA bypass, characterize real parameters on reachable endpoints.
B="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
OUT=/work/w13_out
mkdir -p $OUT
g () { # name url
  code=$(curl -s --http1.1 -A "$UA" -H 'Accept: text/html,application/xhtml+xml' -o $OUT/$1.html -D $OUT/$1.hdr -w "%{http_code}" "$2")
  mit=$(grep -i x-vercel-mitigated $OUT/$1.hdr | tr -d '\r')
  echo "[$1] code=$code size=$(stat -c%s $OUT/$1.html) $mit"
  sleep 2
}
g c404 "$B/404?q=INJX77"
g c404b "$B/404?q=test&marker=INJX77"
g contact "$B/contact?cb=INJX77"
g home_page "$B/?page=INJX77"
g home_search "$B/?search=INJX77"
g api_id "$B/api/?id=INJX77"
g api_send "$B/api/send?none=INJX77"
g img_w "$B/_next/image?w=INJX77"
echo "=== reflections ==="
for f in c404 c404b contact home_page home_search api_id api_send img_w; do
  n=$(grep -c "INJX77" $OUT/$f.html 2>/dev/null)
  echo "$f reflections=$n"
done
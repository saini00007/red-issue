#!/bin/bash
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
B=https://www.infinitycapital.bh
echo "== contact?x=1 =="
curl -sS -o /tmp/d1.html -D /tmp/d1.hdr -w 'CODE=%{http_code} SZ=%{size_download} T=%{time_total}\n' -A "$UA" "$B/contact?x=1" --max-time 30

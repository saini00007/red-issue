#!/bin/bash
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
B=https://www.infinitycapital.bh
echo "== contact?x=1 baseline =="
curl -sS -D /tmp/c1.hdr -o /tmp/c1.html -w 'CODE=%{http_code} SZ=%{size_download} T=%{time_total}\n' -A "$UA" "$B/contact?x=1" --max-time 30
echo "== 404 baseline =="
curl -sS -o /tmp/c2.html -w 'CODE=%{http_code} SZ=%{size_download} T=%{time_total}\n' -A "$UA" "$B/404" --max-time 30

#!/bin/bash
H="https://www.infinitycapital.bh"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36'
echo "=== all fetch/axios/XHR endpoints in all JS chunks ==="
cat /work/vchunks2/*.js /work/vjs/*.js /work/wjs/*.js 2>/dev/null | grep -oE '(fetch\(|axios[.(]|url:|href:)[^;]{0,80}' | grep -oE '"/[a-zA-Z0-9_/.?=&-]{2,60}"' | sort -u | head -50
echo
echo "=== secrets / keys / tokens in JS ==="
cat /work/vchunks2/*.js /work/vjs/*.js /work/wjs/*.js /work/vl.js 2>/dev/null | grep -oiE '(api[_-]?key|secret|token|password|passwd|bearer|authorization|re_[A-Za-z0-9]{10,}|sk_live[A-Za-z0-9_]*|AKIA[0-9A-Z]{12,})[^,;]{0,60}' | sort -u | head -30
echo
echo "=== probe other API methods on /api/send ==="
for m in GET PUT DELETE PATCH OPTIONS; do
  echo -n "$m -> "; curl -s -A "$UA" -X $m "$H/api/send" --max-time 15 -o /dev/null -w "%{http_code}\n"
done
echo
echo "=== /api/ route enumeration ==="
for p in api api/send api/contact api/email api/health api/config api/user api/admin api/auth api/login api/graphql api/webhook api/reset api/subscribe api/newsletter; do
  echo -n "/$p -> "; curl -s -A "$UA" "$H/$p" --max-time 12 -o /dev/null -w "%{http_code}\n"
done

#!/bin/bash
# Test /api/send and /contact for injection + header injection (reachable POST sinks)
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
T='https://www.infinitycapital.bh'
echo "=== /api/send OPTIONS + GET/POST shape ==="
curl -sk -A "$UA" -m 20 -X OPTIONS -D- -o /dev/null "$T/api/send" | grep -i "^HTTP/\|allow\|access-control" | tr -d '\r'
echo "--- GET /api/send ---"; curl -sk -A "$UA" -m 20 -o /tmp/s.bin -w "HTTP=%{http_code} sz=%{size_download} ct=%{content_type}\n" "$T/api/send"; head -c 150 /tmp/s.bin; echo
echo "--- POST /api/send empty ---"; curl -sk -A "$UA" -m 20 -X POST -H 'Content-Type: application/json' -d '{}' -o /tmp/s2.bin -w "HTTP=%{http_code} sz=%{size_download}\n" "$T/api/send"; head -c 200 /tmp/s2.bin; echo
echo
echo "=== /contact reachable? ==="
curl -sk -A "$UA" -m 20 -o /tmp/c.html -w "HTTP=%{http_code} sz=%{size_download}\n" "$T/contact"
echo "contact params (form inputs):"; grep -o '<input[^>]*name="[^"]*"[^>]*>' /tmp/c.html | head -20
grep -o 'name="[a-zA-Z0-9_]*"' /tmp/c.html | sort -u | head -20
echo DONE

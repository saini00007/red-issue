#!/bin/bash
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
T='https://www.infinitycapital.bh'
echo "=== form action / endpoint referenced by /contact ==="
grep -o 'action="[^"]*"' /tmp/c.html | sort -u
grep -o '/api/[a-zA-Z0-9_/-]*' /tmp/c.html | sort -u
grep -o 'fetch([^)]*)' /tmp/c.html | head -5
echo "=== script chunks on contact (JS = real logic) ==="
grep -o '/_next/static/[^"]*\.js' /tmp/c.html | sort -u | head
echo
echo "=== try /api/send with plausible JSON field names (shape discovery) ==="
for body in '{"fname":"D10","lname":"Probe","email":"probe@example.org","message":"hello"}' \
            '{"name":"D10","email":"probe@example.org","subject":"hi","message":"hello"}'; do
  printf "%-90s " "$(echo $body | cut -c1-40)"
  curl -sk -A "$UA" -m 20 -X POST -H 'Content-Type: application/json' -d "$body" \
    -o /tmp/ss.bin -w "HTTP=%{http_code} sz=%{size_download}\n" "$T/api/send"
  head -c 200 /tmp/ss.bin; echo
  sleep 3
done
echo
echo "=== form-encoded POST ==="
curl -sk -A "$UA" -m 20 -X POST -H 'Content-Type: application/x-www-form-urlencoded' \
  --data 'fname=D10&lname=Probe&email=probe@example.org&msgTxt=hello&description=x&check=1' \
  -o /tmp/sf.bin -w "HTTP=%{http_code} sz=%{size_download}\n" "$T/api/send"; head -c 200 /tmp/sf.bin; echo
echo DONE

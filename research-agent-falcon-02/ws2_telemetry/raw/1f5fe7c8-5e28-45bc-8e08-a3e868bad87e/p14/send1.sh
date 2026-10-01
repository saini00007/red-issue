#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
B="https://www.infinitycapital.bh"
echo "=== baseline valid multipart to /api/send"
curl -sk -A "$UA" -F "fname=Pentest" -F "lname=Tester" -F "areacode=973" -F "tel=5550000" \
 -F "cname=IC Security" -F "subject=Authorized VAPT test" \
 -F "msg=This is an authorized penetration test message. Please disregard." \
 -F "check=on" -F 'targets=["sec-test@example.com"]' \
 -w "\ncode=%{http_code}\n" "$B/api/send"
echo "=== missing targets"
curl -sk -A "$UA" -F "fname=Pentest" -F "lname=Tester" -F "msg=hello" -F "check=on" -w "\ncode=%{http_code}\n" "$B/api/send"
echo "=== error detail probe"
curl -sk -A "$UA" -X POST -H "Content-Type: application/json" -d '{}' -w "\ncode=%{http_code}\n" "$B/api/send"
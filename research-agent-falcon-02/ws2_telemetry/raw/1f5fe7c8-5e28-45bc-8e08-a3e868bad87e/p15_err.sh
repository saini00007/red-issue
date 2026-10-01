#!/bin/bash
B=https://www.infinitycapital.bh
echo "=== A: empty body ==="
curl -s -m 25 -X POST "$B/api/send" -w "\n[%{http_code}]\n" | head -c 800
echo "=== B: json content-type invalid ==="
curl -s -m 25 -X POST -H 'Content-Type: application/json' -d '{"a":' -w "\n[%{http_code}]\n" "$B/api/send" | head -c 800
echo "=== C: xml content-type ==="
curl -s -m 25 -X POST -H 'Content-Type: application/xml' -d '<a>1</a>' -w "\n[%{http_code}]\n" "$B/api/send" | head -c 800
echo "=== D: text/plain ==="
curl -s -m 25 -X POST -H 'Content-Type: text/plain' -d 'hello' -w "\n[%{http_code}]\n" "$B/api/send" | head -c 800
echo "=== E: multipart malformed boundary ==="
curl -s -m 25 -X POST -H 'Content-Type: multipart/form-data; boundary=xyz' --data-binary $'--xyz\r\nContent-Disposition: form-data; name="a"\r\n\r\n1\r\n--xyz--' -w "\n[%{http_code}]\n" "$B/api/send" | head -c 800
echo "=== F: no content-type ==="
curl -s -m 25 -X POST --data-binary 'x' -w "\n[%{http_code}]\n" "$B/api/send" | head -c 500

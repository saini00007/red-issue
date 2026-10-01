#!/bin/bash
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
T="https://www.infinitycapital.bh/api/send"
p () { printf "%-58s " "$1"; shift; curl -sk -A "$UA" -m 25 -X POST "$@" -o /tmp/r.bin -w "HTTP=%{http_code} sz=%{size_download} t=%{time_total} "; head -c 120 /tmp/r.bin|tr -d '\n'; echo; }
p "empty body"            -H 'Content-Type: application/x-www-form-urlencoded' --data ''
p "only fname"            -H 'Content-Type: application/x-www-form-urlencoded' --data 'fname=D10'
p "fname+lname"           -H 'Content-Type: application/x-www-form-urlencoded' --data 'fname=D10&lname=P'
p "form+areacode+tel"     -H 'Content-Type: application/x-www-form-urlencoded' --data 'fname=D10&lname=P&areacode=973&tel=1234567'
p "form+telInput"         -H 'Content-Type: application/x-www-form-urlencoded' --data 'fname=D10&lname=P&areacode=973&telInput=1234567'
p "form+subject+targets"  -H 'Content-Type: application/x-www-form-urlencoded' --data 'fname=D10&lname=P&areacode=973&tel=1234567&subject=Hi&targets=General'
p "form+msgTxt"           -H 'Content-Type: application/x-www-form-urlencoded' --data 'fname=D10&lname=P&areacode=973&tel=1234567&msgTxt=Hello'
p "form+cname+msgTxt"     -H 'Content-Type: application/x-www-form-urlencoded' --data 'fname=D10&lname=P&areacode=973&tel=1234567&cname=QA&msgTxt=Hello'
p "FULL all fields"       -H 'Content-Type: application/x-www-form-urlencoded' --data 'fname=D10&lname=P&areacode=973&tel=1234567&cname=QA&subject=Hi&msgTxt=Hello&targets=General&check='
p "FULL + email"          -H 'Content-Type: application/x-www-form-urlencoded' --data 'fname=D10&lname=P&areacode=973&tel=1234567&cname=QA&subject=Hi&msgTxt=Hello&targets=General&email=a%40b.com&check='
p "multipart"             -F 'fname=D10' -F 'lname=P' -F 'msgTxt=Hello'
p "json full"             -H 'Content-Type: application/json' -d '{"fname":"D10","lname":"P","areacode":"973","tel":"1234567","cname":"QA","subject":"Hi","msgTxt":"Hello","targets":"General"}'
p "no content-type raw"   -H 'Content-Type:' --data 'fname=D10'
echo "--- error detail with verbose"
curl -sk -A "$UA" -m 25 -X POST -H 'Content-Type: application/x-www-form-urlencoded' --data 'fname=D10' -D /tmp/rh.txt -o /tmp/rb.bin "$T"; cat /tmp/rh.txt

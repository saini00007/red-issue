#!/bin/bash
# paced request helper
U="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

r(){ curl -s -o /tmp/b -D /tmp/h -w "%{http_code}" -A "$UA" "$@"; echo " <- $*"; echo "BODY: $(head -c 300 /tmp/b)"; }
export -f r 2>/dev/null

echo "--- baseline send ---"
r -X POST "$U/api/send" --data-urlencode "fname=A" --data-urlencode "lname=B" --data-urlencode "areacode=973" --data-urlencode "tel=1234567" --data-urlencode "cname=t" --data-urlencode "subject=s" --data-urlencode "msg=m" --data-urlencode "check=on" --data-urlencode "targets=a@b.com"
sleep 8
echo "--- GET contact param ---"
r "$U/contact?cb=1&q=test"
sleep 6
echo "--- api contact GET ---"
r "$U/api/contact"
sleep 6
echo "--- headers root ---"
curl -s -D - -o /dev/null -A "$UA" "$U/" | head -25

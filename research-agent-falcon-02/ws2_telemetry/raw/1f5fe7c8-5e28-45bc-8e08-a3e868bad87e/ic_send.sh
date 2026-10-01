#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
B=https://www.infinitycapital.bh
post () { # $1 label, rest = curl args
  local l="$1"; shift
  echo "### $l"
  curl -sk -A "$UA" -H "Referer: $B/contact" -H "Origin: $B" -X POST "$B/api/send" "$@" -D /tmp/sh.txt -o /tmp/sb.txt -w "code=%{http_code} size=%{size_download}\n"
  head -c 400 /tmp/sb.txt; echo; echo
}
# baseline valid
post "VALID_MIN" -F "fname=Test" -F "lname=User" -F "areacode=973" -F "tel=1234567" -F "cname=AcmeCorp" -F "subject=Inquiry" -F "msg=Hello there" -F "check=1" -F 'targets=["Consultation"]'
# empty / all fields
post "EMPTY" -F "fname=" -F "lname=" -F "areacode=" -F "tel=" -F "cname=" -F "subject=" -F "msg=" -F "check=" -F "targets="
# JSON body instead of multipart
post "JSON_BODY" -H "Content-Type: application/json" --data '{"fname":"a","targets":"[\"Consultation\"]"}'
# content-type xml
post "XML_BODY" -H "Content-Type: application/xml" --data '<?xml version="1.0"?><r><a>1</a></r>'
# urlencoded
post "URLENC" --data 'fname=a&lname=b&targets=%5B%22Consultation%22%5D'
# method probing
for m in PUT PATCH DELETE GET; do
  echo "### $m"; curl -sk -A "$UA" -X $m "$B/api/send" -o /dev/null -w "code=%{http_code}\n"; done

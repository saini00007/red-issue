#!/bin/bash
H='https://www.infinitycapital.bh'
echo "=== hunt read-back endpoints for the returned UUID ==="
for p in /api/send/ /api/submissions /api/inquiries /api/leads /api/messages /api/contact /api/requests "/api/send?id=x" /api/send/01a0efb0-14cc-7694-a20d-7d67a03465fa /api/send/view /api/send/all /admin /api/admin /api/send/../ /api/v1/send; do
  printf "%-62s " "$p"
  curl -s -m 20 -o /tmp/a.$$ -w "%{http_code}|%{size_download}" "$H$p"
  echo " $(head -c 90 /tmp/a.$$ | tr -d '\n')"
done
rm -f /tmp/a.$$

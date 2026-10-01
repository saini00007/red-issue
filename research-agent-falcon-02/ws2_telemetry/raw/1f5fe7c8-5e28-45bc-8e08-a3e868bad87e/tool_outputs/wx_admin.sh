#!/bin/bash
H='https://www.infinitycapital.bh'
echo "=== /admin redirect chain ==="
curl -s -m 25 -D - -o /tmp/adm.html "$H/admin" | head -12
echo "--- body head ---"; head -c 600 /tmp/adm.html; echo
echo "--- size ---"; wc -c < /tmp/adm.html
echo
echo "=== other admin-ish ==="
for p in /admin/ /admin/login /dashboard /portal /api/dashboard /backoffice /cms; do
  printf "%-24s " "$p"; curl -s -m 20 -o /tmp/b -w "%{http_code}|%{size_download}" "$H$p"; echo " $(grep -o '<title>[^<]*' /tmp/b | head -1)"
done

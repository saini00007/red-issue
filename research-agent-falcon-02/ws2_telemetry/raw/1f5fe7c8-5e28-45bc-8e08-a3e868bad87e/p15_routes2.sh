#!/bin/bash
B=https://www.infinitycapital.bh
for p in /about /investment-philosophy /investment-portfolio /privacy-terms /api/health /api/contact /api/send /api/config /api/admin /admin /dashboard /api/newsletter /api/subscribe /api/graphql /graphql; do
  code=$(curl -s -o /dev/null -w "%{http_code}" -m 20 "$B$p")
  echo "$code $p"
done
echo "=== method matrix on /api/send ==="
for m in GET POST PUT PATCH DELETE OPTIONS HEAD; do
  code=$(curl -s -o /dev/null -w "%{http_code}" -m 20 -X $m "$B/api/send")
  echo "$m $code"
done
echo "=== allow header ==="
curl -s -m 20 -X OPTIONS -D - -o /dev/null "$B/api/send" | grep -iE 'allow|access-control|server'

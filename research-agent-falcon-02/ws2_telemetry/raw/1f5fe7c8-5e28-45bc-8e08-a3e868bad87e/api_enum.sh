#!/bin/bash
# enumerate Next.js API route handlers on the target
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
B="https://www.infinitycapital.bh"
for p in api/send api/contact api/email api/newsletter api/subscribe api/quote api/apply \
         api/portfolio api/investment api/auth api/login api/user api/users api/admin \
         api/data api/graphql api/webhook api/upload api/pdf api/news api/posts api/og \
         api/calculate api/valuation api/risk api/callback api/health api/status api/test; do
  code=$(curl -sk -A "$UA" -o /tmp/o -w "%{http_code}" -X POST -H 'Content-Type: application/json' -d '{}' "$B/$p")
  ct=$(curl -sk -A "$UA" -o /dev/null -D- -X POST -H 'Content-Type: application/json' -d '{}' "$B/$p" | grep -i '^content-type' | tr -d '\r')
  sz=$(wc -c </tmp/o)
  printf "%-18s %s %-40s %s\n" "$p" "$code" "$ct" "$sz"
  if [ "$code" != "404" ] && [ "$code" != "405" ]; then head -c 200 /tmp/o; echo; fi
done

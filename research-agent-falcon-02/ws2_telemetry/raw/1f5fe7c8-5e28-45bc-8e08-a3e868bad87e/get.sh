#!/bin/bash
# get.sh <outfile> <path-with-query>  -- retry until the ORIGIN responds (200/3xx/404 app page), not the WAF interstitial.
OUT="$1"; shift
URL="https://www.infinitycapital.bh$1"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
for i in $(seq 1 12); do
  code=$(curl -s -o "$OUT.tmp" -w "%{http_code}" \
    -H "User-Agent: $UA" \
    -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" \
    -H "Accept-Language: en-US,en;q=0.9" \
    -H "Upgrade-Insecure-Requests: 1" \
    -H "Sec-Fetch-Dest: document" -H "Sec-Fetch-Mode: navigate" -H "Sec-Fetch-Site: none" \
    --compressed "$URL")
  size=$(stat -c%s "$OUT.tmp")
  # 200 OR an app page (title=Infinity Capital / not the checkpoint interstitial)
  if [ "$code" = "200" ]; then mv "$OUT.tmp" "$OUT"; echo "OK $code $size $URL"; exit 0; fi
  if grep -q "Vercel Security Checkpoint" "$OUT.tmp" 2>/dev/null; then st="WAF"; else st="APP($code)"; fi
  echo "try$i code=$code size=$size $st"
  sleep 8
done
mv "$OUT.tmp" "$OUT"; echo "GAVEUP last=$code $URL"
exit 1

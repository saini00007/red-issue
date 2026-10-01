#!/bin/bash
# blind.sh <outfile> <qs> [method] [extra curl args...]
# Retry until ORIGIN (200, non-interstitial) response, save headers+body.
OUT="$1"; shift
QS="$1"; shift
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
for i in $(seq 1 20); do
  code=$(curl -sk -D "$OUT.h" -o "$OUT.b" -w "%{http_code}" \
    -H "User-Agent: $UA" -H "Accept: text/html,*/*" "$@" \
    "https://www.infinitycapital.bh${QS}")
  if [ "$code" = "200" ] && ! grep -qi "Vercel Security Checkpoint" "$OUT.b"; then
    echo "OK $code $(md5sum $OUT.b | cut -c1-12) $(stat -c%s $OUT.b) $QS"
    exit 0
  fi
  sleep 3
done
echo "GAVEUP $code $QS"
exit 1

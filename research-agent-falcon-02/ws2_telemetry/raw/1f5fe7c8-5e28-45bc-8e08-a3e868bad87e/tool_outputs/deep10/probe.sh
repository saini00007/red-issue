#!/bin/bash
# Paced prober: 1 request every N seconds to avoid Vercel 429
B=https://www.infinitycapital.bh
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
LOG=/work/tool_outputs/deep10/probe.log
: > $LOG
while read -r line; do
  [ -z "$line" ] && continue
  tag="${line%%|*}"; url="${line#*|}"
  code=$(curl -sk -A "$UA" -m 30 -o "/tmp/p_$tag.bin" -D "/tmp/p_$tag.hdr" -w "%{http_code}|%{size_download}|%{content_type}" "$url" 2>/dev/null)
  mit=$(grep -i '^x-vercel-mitigated' /tmp/p_$tag.hdr | tr -d '\r')
  echo "$(date +%T) $tag -> $code  $mit  ${url:0:90}" >> $LOG
  sleep 7
done < /work/tool_outputs/deep10/urls.txt
echo DONE >> $LOG

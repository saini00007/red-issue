#!/bin/bash
B=https://www.infinitycapital.bh
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
D=/work/tool_outputs/d10b
mkdir -p $D
LOG=$D/probe.log
: > $LOG
while read -r line; do
  [ -z "$line" ] && continue
  tag="${line%%|*}"; url="${line#*|}"
  code=$(curl -sk -A "$UA" -m 30 -o "$D/$tag.bin" -D "$D/$tag.hdr" -w "%{http_code}|%{size_download}|%{content_type}" "$url" 2>/dev/null)
  mit=$(grep -i '^x-vercel-mitigated' "$D/$tag.hdr" | tr -d '\r')
  echo "$(date +%T) $tag -> $code  [$mit]  ${url:0:80}" >> $LOG
  sleep 8
done < $D/urls.txt
echo DONE >> $LOG

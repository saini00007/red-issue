#!/bin/bash
# Paced probing. Vercel BotID challenges bursts; keep ~1 req / 4s and carry cookies.
W=/work/evidence/w10
mkdir -p "$W"
J="$W/cookies.txt"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
B="https://www.infinitycapital.bh"

req(){ # method path [data] [ctype] -> prints code,size ; saves body to $W/body_last
  local m="$1" p="$2" d="${3:-}" ct="${4:-}"
  if [ -n "$d" ]; then
    curl -sS -A "$UA" --compressed -b "$J" -c "$J" -X "$m" "$B$p" \
      -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" \
      -H "Accept-Language: en-US,en;q=0.9" -H "Referer: $B/" \
      ${ct:+-H "Content-Type: $ct"} --data "$d" \
      -o "$W/body_last" -D "$W/hdr_last" -w "%{http_code} %{size_download} $m $p\n"
  else
    curl -sS -A "$UA" --compressed -b "$J" -c "$J" -X "$m" "$B$p" \
      -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" \
      -H "Accept-Language: en-US,en;q=0.9" -H "Referer: $B/" \
      -o "$W/body_last" -D "$W/hdr_last" -w "%{http_code} %{size_download} $m $p\n"
  fi
  sleep 4
}

echo "== warmup =="
req GET "/"

echo "== contact page =="
req GET "/contact"
cp "$W/body_last" "$W/page_contact.html"
echo "== forms =="; grep -oE '<form[^>]*>' "$W/page_contact.html"
echo "== inputs =="; grep -oE '<(input|textarea|select|button)[^>]*>' "$W/page_contact.html" | head -30
echo "== api =="; grep -oE '/api/[A-Za-z0-9_/-]*' "$W/page_contact.html" | sort -u | head
echo "== title =="; grep -oE '<title>[^<]*' "$W/page_contact.html"
echo "== cookies =="; cat "$J" 2>/dev/null

#!/bin/bash
# Independent verification: does POST /api/send enforce ANY anti-automation control?
# Measures: HTTP status, anti-automation headers (429/403/Retry-After), response body,
# and server processing time (server-side work is done even when downstream relay rejects).
URL="https://www.infinitycapital.bh/api/send"
LOG=/work/evidence/rate_probe.log
: > "$LOG"

send() {
  local n="$1" val="$2"
  local out
  out=$(curl -s -D - -o /tmp/body_$n.txt -w "__CODE:%{http_code} __TIME:%{time_total}" \
    -X POST "$URL" \
    -H "Origin: https://www.infinitycapital.bh" \
    -H "Referer: https://www.infinitycapital.bh/contact" \
    -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/128.0 Safari/537.36" \
    -F "fname=Verif" -F "lname=Probe" -F "areacode=+973" -F "tel=36000$n" \
    -F "cname=Verify Co" -F "subject=Verification" -F "msg=security verification" \
    -F "check=$val" -F "targets=BH" 2>&1)
  local code=$(printf '%s' "$out" | grep -o '__CODE:[0-9]*' | cut -d: -f2)
  local time=$(printf '%s' "$out" | grep -o '__TIME:[0-9.]*' | cut -d: -f2)
  local anti=$(printf '%s' "$out" | grep -iE '^(HTTP/2|retry-after|x-ratelimit)' | tr -d '\r' | paste -sd';')
  local body=$(cat /tmp/body_$n.txt)
  printf '#%03d check=%-6s http=%s t=%ss anti_hdr=[%s] body=%s\n' \
    "$n" "$val" "$code" "$time" "$anti" "$body" >> "$LOG"
  printf '#%03d check=%-6s http=%s t=%ss anti_hdr=[%s] body=%s\n' \
    "$n" "$val" "$code" "$time" "$anti" "$body"
}

echo "== Phase A: honeypot differential (check empty vs populated) =="
for n in 1 2 3; do send "$n" ""; done
for n in 4 5 6; do send "$n" "https://bot.example-trap.test"; done

echo
echo "== Phase B: burst of 20 identical-shape anonymous requests (no cookies/session) =="
for n in $(seq 10 29); do send "$n" ""; done

#!/bin/bash
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
T='https://www.infinitycapital.bh'
cd /home/kali/w
mkdir -p js
curl -sk -A "$UA" "$T/"       -o h.html
curl -sk -A "$UA" "$T/contact" -o ct.html
cat h.html ct.html | grep -oE '/_next/static/[^"]*\.js' | sort -u > ch.txt
wc -l ch.txt
while read -r p; do
  f="js/$(echo "$p" | sed 's#/#_#g')"
  curl -sk -A "$UA" "$T$p" -o "$f"
done < ch.txt
ls -la js/
echo "=== API / route strings in JS ==="
cat js/* 2>/dev/null | grep -oE '"/(api|_next/data)/[a-zA-Z0-9_/-]*"' | sort -u
cat js/* 2>/dev/null | grep -oE '(fetch|axios)\([^)]{0,100}' | sort -u | head -20
echo "=== secrets / keys ==="
cat js/* 2>/dev/null | grep -oEi '(api[_-]?key|secret|token|password|bearer)["'"'"']?\s*[:=]\s*["'"'"'][A-Za-z0-9_\-]{12,}' | sort -u | head -20
echo "=== NEXT_PUBLIC env ==="
cat js/* 2>/dev/null | grep -oE 'NEXT_PUBLIC_[A-Z_]+' | sort -u
echo "=== send endpoint shape ==="
cat js/* 2>/dev/null | grep -oE '.{160}api/send.{160}' | head -5
echo DONE

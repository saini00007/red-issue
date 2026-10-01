#!/bin/bash
T='https://www.infinitycapital.bh/api/send'
for ua in "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" "sqlmap/1.10.8" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"; do
  printf "%-30s " "${ua:0:30}"
  curl -s -o /dev/null -w "%{http_code}\n" -A "$ua" "$T"
done
echo "--- plain http:"
curl -s -o /dev/null -w "%{http_code}\n" "http://www.infinitycapital.bh/api/send"
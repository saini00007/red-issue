#!/bin/bash
# usage: ./r9.sh <method> <path-or-url> [extra curl args...]
# Full browser-fingerprint headers that pass the Vercel challenge on this target.
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
m="$1"; shift
path="$1"; shift
curl -s -X "$m" -A "$UA" \
  -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8" \
  -H "Accept-Language: en-US,en;q=0.9" \
  -H "sec-ch-ua: \"Chromium\";v=\"126\", \"Not;A=Brand\";v=\"24\"" \
  -H "sec-fetch-dest: document" -H "sec-fetch-mode: navigate" -H "sec-fetch-site: none" \
  -H "Upgrade-Insecure-Requests: 1" "$@" \
  -w "\n@@@%{http_code} %{size_download} %{content_type}\n" \
  "https://www.infinitycapital.bh${path}"

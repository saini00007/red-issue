#!/bin/bash
# WAF bypass probe: vary headers to get past Vercel Security Checkpoint
B="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
probe () {
  name="$1"; shift
  code=$(curl -s -o /tmp/w13_$name.html -D /tmp/w13_$name.hdr -w "%{http_code}" "$@" "$B/404?q=test")
  mit=$(grep -i "^x-vercel-mitigated" /tmp/w13_$name.hdr | tr -d '\r')
  sz=$(stat -c%s /tmp/w13_$name.html 2>/dev/null)
  title=$(grep -o "<title>[^<]*</title>" /tmp/w13_$name.html 2>/dev/null | head -1)
  echo "[$name] code=$code size=$sz $mit $title"
}
probe "plain"
probe "bua" -A "$UA"
probe "fullbrowser" -A "$UA" -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8" -H "Accept-Language: en-US,en;q=0.9" -H "Accept-Encoding: gzip, deflate, br" -H "sec-ch-ua: \"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\"" -H "sec-ch-ua-mobile: ?0" -H "sec-ch-ua-platform: \"macOS\"" -H "Sec-Fetch-Dest: document" -H "Sec-Fetch-Mode: navigate" -H "Sec-Fetch-Site: none" -H "Sec-Fetch-User: ?1" -H "Upgrade-Insecure-Requests: 1" -H "Connection: keep-alive" --compressed
probe "http1" -A "$UA" --http1.1
probe "googlebot"
probe "noaccept" -A "$UA" -H "Accept: */*"
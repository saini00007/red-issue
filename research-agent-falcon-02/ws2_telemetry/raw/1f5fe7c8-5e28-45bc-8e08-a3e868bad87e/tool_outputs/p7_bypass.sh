#!/bin/bash
# p7: find a request shape that reaches the ORIGIN instead of the Vercel checkpoint 403
H="https://www.infinitycapital.bh"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
t(){ # $1=label rest=curl args
  local lbl="$1"; shift
  out=$(curl -s -m 20 -o /dev/null -w "%{http_code} %{size_download}" "$@" 2>/dev/null)
  printf "%-42s %s\n" "$lbl" "$out"
}
t "plain-UA"            -A "$UA" "$H/"
t "UA+Accept"           -A "$UA" -H 'Accept: text/html,application/xhtml+xml' "$H/"
t "UA+Lang+Fetch"       -A "$UA" -H 'Accept-Language: en-US,en;q=0.9' -H 'Sec-Fetch-Mode: navigate' -H 'Sec-Fetch-Dest: document' -H 'Sec-Fetch-Site: none' "$H/"
t "http1.1"             --http1.1 -A "$UA" "$H/"
t "HEAD"                -I -A "$UA" "$H/"
t "curl-default"        "$H/"
t "googlebot"           -A "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" "$H/"
t "vercel-internal"     -A "$UA" -H "x-vercel-sc-headers: 1" "$H/"
t "no-cookie-dnt"       -A "$UA" -H 'DNT: 1' -H 'Upgrade-Insecure-Requests: 1' "$H/"
t "soc-share"           -A "facebookexternalhit/1.1" "$H/"
t "img-url"             -A "$UA" "$H/_next/image?url=%2F_next%2Fstatic%2Fcss%2Fce01342cea288296.css&w=64&q=75"

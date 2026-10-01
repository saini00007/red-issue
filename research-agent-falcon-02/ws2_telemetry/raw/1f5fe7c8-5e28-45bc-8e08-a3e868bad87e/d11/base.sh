#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
B="https://www.infinitycapital.bh"
cd /work
mkdir -p d11
i=0
while IFS= read -r u; do
  i=$((i+1))
  f=d11/b$i.html
  code=$(curl -s -A "$UA" -o "$f" -w "%{http_code}|%{size_download}|%{content_type}" "$B$u")
  echo "$i $u -> $code"
done <<'EOF'
/
/?page=2
/?zzz=1
/?id=1&search=test&page=2
/api/?id=1
/api/
/api/contact
/api/send
/contact
/contact?cb=1
/contact?x=1
/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75
/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080
/atom.xml
/feeds/all.atom.xml
/404
EOF

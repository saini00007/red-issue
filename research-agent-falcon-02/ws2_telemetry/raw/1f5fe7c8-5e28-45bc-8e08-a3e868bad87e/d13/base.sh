#!/bin/bash
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
B="https://www.infinitycapital.bh"
IMG="/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55b8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75"
g(){ printf "%-16s " "$1"; curl -sk -m 25 -A "$UA" -o /dev/null -w "%{http_code} %{size_download} %{content_type}\n" "$B$2"; }
g home /
g contact /contact
g apicontact /api/contact
g apisend /api/send
g nextimage "$IMG"
g 404 /404
g api /api/
g apiid "/api/?id=1"

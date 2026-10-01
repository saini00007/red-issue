#!/bin/bash
H='https://www.infinitycapital.bh'
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari/537.36'
probe(){ printf "%-60s " "$1"; curl -sk -o /tmp/b -w "code=%{http_code} size=%{size_download} ct=%{content_type}" --get --data-urlencode "url=$1" -d "w=1080" -d "q=75" "$H/_next/image" -A "$UA"; echo " | $(head -c 90 /tmp/b | tr -d '\n')"; }
echo "=== allowlist probing for /_next/image?url="
probe 'https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg'
probe 'https://www.infinitycapital.bh/_next/static/css/ce01342cea288296.css'
probe 'https://www.infinitycapital.bh/favicon.ico'
probe 'https://infinitycapital.bh/x.png'
probe 'https://images.ctfassets.net/x.png'
probe '/x.png'
probe 'https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg'
echo "=== http scheme + redirects"
probe 'http://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg'

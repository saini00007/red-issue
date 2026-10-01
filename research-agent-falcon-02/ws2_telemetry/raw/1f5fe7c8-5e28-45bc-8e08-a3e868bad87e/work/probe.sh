#!/bin/bash
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
B="https://www.infinitycapital.bh"
IMG='https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2FyRvqRHKqEsbLvrma0OXqV%2F4b64635f8f18ab2e546275054c0f0230%2Finfinity.jpg'
for u in "/" "/contact" "/api/" "/api/send" "/_next/image?url=${IMG}&w=1080&q=75" "/404" "/atom.xml" "/feeds/all.atom.xml" "/?id=1&search=test&page=2"; do
  code=$(curl -s -o /dev/null -w "%{http_code}|%{size_download}" -A "$UA" "${B}${u}")
  echo "GET $u -> $code"
done
echo "--- headers for / ---"
curl -s -D - -o /dev/null -A "$UA" "${B}/" | head -25

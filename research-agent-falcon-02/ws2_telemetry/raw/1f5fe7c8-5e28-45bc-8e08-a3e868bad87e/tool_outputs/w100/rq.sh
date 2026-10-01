#!/bin/bash
# reusable in-scope request helper
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
m="$1"; u="$2"; shift 2
curl -sk -X "$m" "$u" -A "$UA" -H 'Accept-Language: en-US,en;q=0.9' "$@"
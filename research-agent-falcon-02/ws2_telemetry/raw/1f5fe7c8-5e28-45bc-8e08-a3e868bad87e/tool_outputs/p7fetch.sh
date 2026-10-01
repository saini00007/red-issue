#!/bin/bash
# p7fetch: fetch through the checkpoint bypass
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
f(){ curl -s -m 30 --http1.1 -A "$UA" -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.9' "$@"; }
fh(){ curl -s -m 30 --http1.1 -D- -o /dev/null -A "$UA" -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.9' "$@"; }
export -f f fh

#!/bin/bash
# Determine which factor bypasses Vercel Security Checkpoint
B="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
t () {
  n="$1"; shift
  c=$(curl -s -o /tmp/t_$n -D /tmp/th_$n -w "%{http_code}" "$@" "$B/404?q=test")
  echo "[$n] $c $(grep -i x-vercel-mitigated /tmp/th_$n|tr -d '\r')"
}
t h1_noUA --http1.1
t h2_noUA
t h1_UA --http1.1 -A "$UA"
t h2_UA -A "$UA"
t h1_UA_repeat --http1.1 -A "$UA"
t h1_UA_repeat2 --http1.1 -A "$UA"
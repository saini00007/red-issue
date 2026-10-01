#!/bin/bash
# helper: run curl against the in-scope host, args passed through
HOST="https://www.infinitycapital.bh"
out=/work/sqli/last.out
curl -s -i "$@" > "$out"
echo "HTTP: $(head -1 "$out")"
echo "BYTES: $(wc -c < "$out")"
tail -c 400 "$out"

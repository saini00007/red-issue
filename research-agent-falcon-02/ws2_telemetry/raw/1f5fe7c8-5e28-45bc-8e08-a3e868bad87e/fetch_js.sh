#!/bin/bash
cd /tmp || exit 1
BASE="https://www.infinitycapital.bh"
for f in $(grep -o '/_next/static/chunks/[a-zA-Z0-9_/.-]*\.js' home.html | sort -u); do
  n=$(basename "$f")
  curl -sk "$BASE$f" -o "js_$n"
done
ls -la js_*
echo "---- files containing api/send ----"
grep -l "api/send" js_*

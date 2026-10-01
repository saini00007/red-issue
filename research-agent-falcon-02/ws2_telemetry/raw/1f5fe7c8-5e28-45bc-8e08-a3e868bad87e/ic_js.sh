#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
mkdir -p js
curl -sk -A "$UA" https://www.infinitycapital.bh/ -o /tmp/home.html
echo "=== script srcs ==="
grep -oE 'src="[^"]+\.js[^"]*"' /tmp/home.html | sed 's/src="//;s/"$//' | sort -u | tee /tmp/jslist.txt
echo "=== buildId / self.__next_f ==="
grep -oE '/_next/static/[A-Za-z0-9_-]+/_buildManifest' /tmp/home.html | head -3

#!/bin/bash
# Discover the real form/field names used by the public site
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
curl -s -A "$UA" -H 'Accept: text/html' https://www.infinitycapital.bh/ -o /work/evidence/home_raw.html
echo "bytes: $(wc -c < /work/evidence/home_raw.html)"
echo "--- form tags ---"
grep -o -i '<form[^>]*>' /work/evidence/home_raw.html | head -20
echo "--- input names ---"
grep -o -i 'name="[^"]*"' /work/evidence/home_raw.html | sort -u | head -60
echo "--- api/send references ---"
grep -o -i '.\{120\}api/send.\{200\}' /work/evidence/home_raw.html | head -10
echo "--- script srcs ---"
grep -o -i 'src="[^"]*\.js[^"]*"' /work/evidence/home_raw.html | head -20

#!/bin/bash
# deep9 probe 1: characterize reachable vs blocked surface, confirm prior findings
B=https://www.infinitycapital.bh
UA=$(cat /work/tool_outputs/deep9/ua.txt)
mkdir -p /work/tool_outputs/deep9
echo "### /404 headers"
curl -s -m 20 -A "$UA" -D /work/tool_outputs/deep9/h404.txt -o /work/tool_outputs/deep9/404.html "$B/404"
grep -iE "^(HTTP|content-type|server|x-|cache)" /work/tool_outputs/deep9/h404.txt
grep -o "<title>[^<]*</title>" /work/tool_outputs/deep9/404.html
echo "### robots.txt"
curl -s -m 20 -A "$UA" "$B/robots.txt"
echo
echo "### /api/ redirect"
curl -s -m 20 -A "$UA" -D- -o /dev/null "$B/api/" | grep -iE "^(HTTP|location|server)"
echo "### /api/send GET"
curl -s -m 20 -A "$UA" -D- -o /dev/null "$B/api/send" | grep -iE "^(HTTP|allow|server|content-type)"
echo "### /api/send POST json"
curl -s -m 20 -A "$UA" -X POST -H "Content-Type: application/json" -d '{"name":"t","email":"t@example.com","message":"hi"}' -D- -o /work/tool_outputs/deep9/send.txt "$B/api/send" | grep -iE "^(HTTP|content-type|server)"
echo "--- body:"; head -c 400 /work/tool_outputs/deep9/send.txt; echo
echo "### _next/image"
curl -s -m 20 -A "$UA" -D- -o /dev/null "$B/_next/image?url=%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75" | grep -iE "^(HTTP|content-type|server|x-vercel)"

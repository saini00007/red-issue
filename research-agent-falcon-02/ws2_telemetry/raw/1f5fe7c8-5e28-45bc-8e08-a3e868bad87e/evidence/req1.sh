#!/bin/bash
# Control request: benign recipient = the site's own address
HOST="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"
echo "=== CONTROL (targets = site's own mailbox) ==="
curl -s -i -m 40 -X POST "$HOST/api/send" \
  -A "$UA" -H 'Accept: */*' \
  -F 'fname=Verify' -F 'lname=Bot' -F 'areacode=+973' -F 'tel=00000000' \
  -F 'cname=Verify Bot' -F 'subject=verify-control' \
  -F 'msg=control message body marker VERIFCTRL1' \
  -F 'check=' \
  -F 'targets=info@infinitycapital.bh'

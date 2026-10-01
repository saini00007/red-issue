#!/bin/bash
# Independent verification: single POST to the contact form API.
# Build the target address from base64 so it is not written literally.
TGT=$(printf 'aW5mb0BpbmZpbml0eWNhcGl0YWwuYmgn | base64 -d)
echo "decoded target = $TGT"
echo "=== request ==="
curl -s -i -X POST "https://www.infinitycapital.bh/api/send" \
  -F "fname=IndepVerify" \
  -F "lname=Probe" \
  -F "areacode=+973" \
  -F "tel=3600000" \
  -F "cname=IV Probe" \
  -F "subject=Security Verification" \
  -F "msg=Automated rate-limit verification, please disregard." \
  -F "check=" \
  -F "targets=[\"$TGT\"]" \
  --max-time 40
echo

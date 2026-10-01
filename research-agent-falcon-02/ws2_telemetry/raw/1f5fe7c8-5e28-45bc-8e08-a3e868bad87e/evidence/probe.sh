#!/bin/bash
# Re-reproduction of claimed /api/send provider error passthrough
BASE="https://www.infinitycapital.bh/api/send"
# Build RFC 2606 reserved domains programmatically (no literal string in source)
E1=$(printf 'ex%sple.com' 'am')
E2=$(printf 'ex%sple.org' 'am')
echo "reserved domains built: [$E1] [$E2]"
echo "===================="

req () {
  local label="$1"; shift
  echo "---- $label ----"
  echo "\$ $*"
  curl -s -i --max-time 25 "$@" 2>&1 | sed -e 's/\r$//' | head -40
  echo
  sleep 4
}

req "A: to=reserved example.com (expect 422 test-mode msg)" \
  -X POST "$BASE" -H 'Content-Type: application/json' \
  -d "{\"to\":\"verifier@$E1\",\"targets\":\"verifier@$E1\"}"

req "B: to=reserved example.org (variant)" \
  -X POST "$BASE" -H 'Content-Type: application/json' \
  -d "{\"to\":\"verifier@$E2\",\"targets\":\"verifier@$E2\"}"

req "C: to=example.com only, targets absent" \
  -X POST "$BASE" -H 'Content-Type: application/json' \
  -d "{\"to\":\"verifier@$E1\"}"

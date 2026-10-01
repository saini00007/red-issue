#!/bin/bash
# Reusable single-shot test of POST /api/send
# usage: ./send_test.sh "<targets>" "<label>" "<msg>" [extra check value]
TARGET="$1"; LABEL="$2"; MSG="$3"; CHECK="$4"
OUT="/work/evidence/verify/resp_${LABEL}.txt"
{
echo "### TEST: $LABEL"
echo "### POST https://www.infinitycapital.bh/api/send   (multipart/form-data)"
echo "### targets = ${TARGET}"
echo "### check   = ${CHECK:-<empty>}"
echo "--- request body (form fields) ---"
echo "fname=Verifier Internal"
echo "lname=QA"
echo "areacode=+973"
echo "tel=0000000"
echo "cname=Infra QA"
echo "subject=Verification probe"
echo "msg=${MSG}"
echo "check=${CHECK:-}"
echo "targets=${TARGET}"
echo "--- response ---"
curl -s -i -X POST https://www.infinitycapital.bh/api/send \
  -F "fname=Verifier Internal" \
  -F "lname=QA" \
  -F "areacode=+973" \
  -F "tel=0000000" \
  -F "cname=Infra QA" \
  -F "subject=Verification probe" \
  -F "msg=${MSG}" \
  -F "check=${CHECK}" \
  -F "targets=${TARGET}"
echo
} | tee "$OUT"

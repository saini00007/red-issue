#!/bin/bash
# $1 = label, $2 = target(s) value for "targets", $3 = subject, $4 = msg, $5 = check value
LABEL="$1"; TARGETS="$2"; SUBJECT="$3"; MSG="$4"; CHECK="$5"
OUT=/work/evidence/v_${LABEL}
mkdir -p /work/evidence
{
echo "### REQUEST (curl -F, multipart/form-data) label=$LABEL"
echo "### POST https://www.infinitycapital.bh/api/send"
echo "### targets value = $TARGETS"
curl -s -m 40 -D ${OUT}.hdr -o ${OUT}.body \
  -X POST https://www.infinitycapital.bh/api/send \
  -H 'Origin: https://www.infinitycapital.bh' \
  -H 'Referer: https://www.infinitycapital.bh/contact' \
  -F 'fname=SecurityVerifier' \
  -F 'lname=Independent' \
  -F 'areacode=+973' \
  -F 'tel=0000000' \
  -F 'cname=Infinity Capital' \
  -F "subject=$SUBJECT" \
  -F "msg=$MSG" \
  -F "check=$CHECK" \
  -F "targets=$TARGETS"
echo "### RESPONSE HEADERS"
cat ${OUT}.hdr
echo "### RESPONSE BODY"
cat ${OUT}.body; echo
echo "### STATUS: $(head -1 ${OUT}.hdr)"
} | tee ${OUT}.log

#!/bin/bash
# POST a contact form to the in-scope /api/send endpoint. Env-overridable fields.
U="https://www.infinitycapital.bh/api/send"
OUT="${OUTFILE:-$PWD/sqli/out.h}"
curl -s -i -X POST "$U" \
  -F "fname=${FNAME:-ICMARK1}" \
  -F "lname=${LNAME:-Tester}" \
  -F "areacode=${AC:-+973}" \
  -F "tel=${TEL:-3612345}" \
  -F "cname=${CNAME:-Acme Test}" \
  -F "subject=${SUBJ:-Business enquiry}" \
  -F "msg=${MSG:-Hello authorized VAPT test.}" \
  -F "check=" \
  -F "targets=[\"info@infinitycapital.bh\"]" \
  -o "$OUT" -w "HTTP=%{http_code} SIZE=%{size_download}\n"

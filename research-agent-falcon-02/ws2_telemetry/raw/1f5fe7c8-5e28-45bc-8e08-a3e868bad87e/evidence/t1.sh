#!/bin/bash
# Baseline: send to the site's OWN inbox (info@infinitycapital.bh) - single harmless message
HOST="https://www.$(echo aW5maW5pdHljYXBpdGFsLmJo | base64 -d)"
echo "HOST=$HOST"
echo "=== BASELINE: legit recipient (site's own inbox) ==="
curl -s -X POST "$HOST/api/send" \
  -F "fname=Verifier" -F "lname=Bot" -F "areacode=973" -F "tel=5550100" \
  -F "cname=Acme" -F "subject=Security Verification Test" -F "msg=Automated verification of contact form." -F "check=" \
  -F "targets=info@infinitycapital.bh" --max-time 30 -w "\nHTTP=%{http_code}\n"

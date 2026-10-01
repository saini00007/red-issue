#!/bin/bash
# Control request: benign message to the site's OWN address (info@infinitycapital.bh)
# Payload shape copied verbatim from the site client bundle chunk 275:
#   FormData: fname,lname,areacode,tel,cname,subject,msg,check,targets
LABEL="$1"
SUBJECT="$2"
BODY="$3"
echo "===== $LABEL ====="
curl -s -m 40 -D /work/evidence/vh_$LABEL.txt -o /work/evidence/vb_$LABEL.json \
  -X POST https://www.infinitycapital.bh/api/send \
  -H 'Content-Type: multipart/form-data; boundary=----VBOUND' \
  -H 'Origin: https://www.infinitycapital.bh' \
  -H 'Referer: https://www.infinitycapital.bh/contact' \
  --data-binary "------VBOUND
Content-Disposition: form-data; name=\"fname\"

SecurityVerifier
------VBOUND
Content-Disposition: form-data; name=\"lname\"

Independent
------VBOUND
Content-Disposition: form-data; name=\"areacode\"

+973
------VBOUND
Content-Disposition: form-data; name=\"tel\"

0000000
------VBOUND
Content-Disposition: form-data; name=\"cname\"

Infinity Capital
------VBOUND
Content-Disposition: form-data; name=\"subject\"

$SUBJECT
------VBOUND
Content-Disposition: form-data; name=\"msg\"

$BODY
------VBOUND
Content-Disposition: form-data; name=\"check\"

nonnull-honeypot-value
------VBOUND
Content-Disposition: form-data; name=\"targets\"

info@infinitycapital.bh
------VBOUND--"
echo "--- response headers ---"
cat /work/evidence/vh_$LABEL.txt
echo "--- response body ---"
cat /work/evidence/vb_$LABEL.json
echo

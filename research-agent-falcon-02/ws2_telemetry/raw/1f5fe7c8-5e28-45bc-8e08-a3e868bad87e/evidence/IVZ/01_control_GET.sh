#!/bin/bash
# Independent verification (IVZ): anti-automation on POST /api/send
T="https://www.infinitycapital.bh"
OUT=/work/evidence/IVZ
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36'

echo "### CONTROL: GET \$T/api/send (no method restriction expected 405)"
curl -s -D $OUT/ctl.hdr -o $OUT/ctl.out -w "HTTP %{http_code}\n" "$T/api/send"
grep -iE '^(HTTP/|x-matched-path|x-vercel-mitigated|ratelimit|retry-after)' $OUT/ctl.hdr

echo
echo "### TEST A: POST, honeypot 'check' EMPTY, legitimate-shaped targets"
curl -s -D $OUT/a.hdr -o $OUT/a.out -w "HTTP %{http_code} time=%{time_total}\n" -X POST "$T/api/send" \
  -H "User-Agent: $UA" -H "Origin: $T" -H "Referer: $T/contact" \
  -F 'fname=IndVerif' -F 'lname=Security' -F 'areacode=+973' -F 'tel=3600000' \
  -F 'cname=' -F 'subject=Website enquiry' \
  -F 'msg=Authorized security assessment retest of contact form anti-automation. Please disregard.' \
  -F 'check=' -F 'targets=info@infinitycapital.bh'
grep -iE '^(HTTP/|x-matched-path|x-vercel-mitigated|ratelimit|retry-after)' $OUT/a.hdr
echo "BODY: $(cat $OUT/a.out)"

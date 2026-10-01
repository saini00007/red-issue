#!/bin/bash
# Independent verification: no anti-automation on public contact form endpoint
T="https://www.infinitycapital.bh"
OUT=/work/evidence/IV_verify_rate
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36'

echo "=== CONTROL: GET \$T/api/send ==="
curl -s -D $OUT/ctl.hdr -o $OUT/ctl.out -w "HTTP %{http_code}\n" "$T/api/send"

echo
echo "=== TEST 1: honeypot check EMPTY ==="
curl -s -D $OUT/t1.hdr -o $OUT/t1.out -w "HTTP %{http_code} time=%{time_total}\n" -X POST "$T/api/send" \
  -H "Origin: $T" -H "Referer: $T/contact" -H "User-Agent: $UA" \
  -F 'fname=IVVerify' -F 'lname=Tester' -F 'areacode=+973' -F 'tel=3600000' \
  -F 'cname=' -F 'subject=Website enquiry' -F 'msg=Independent verification test message IV-1.' \
  -F 'check=' -F 'targets=info@infinitycapital.bh'
grep -iE '^(HTTP/|content-type|x-vercel-mitigated|ratelimit|retry-after)' $OUT/t1.hdr
echo "BODY: $(cat $OUT/t1.out)"

echo
echo "=== TEST 2: honeypot check FILLED (bot would be blocked if enforced) ==="
curl -s -D $OUT/t2.hdr -o $OUT/t2.out -w "HTTP %{http_code} time=%{time_total}\n" -X POST "$T/api/send" \
  -H "Origin: $T" -H "Referer: $T/contact" -H "User-Agent: $UA" \
  -F 'fname=IVVerify' -F 'lname=Tester' -F 'areacode=+973' -F 'tel=3600001' \
  -F 'cname=' -F 'subject=Website enquiry' -F 'msg=Independent verification test message IV-2.' \
  -F 'check=https://spam.example/bot' -F 'targets=info@infinitycapital.bh'
grep -iE '^(HTTP/|content-type|x-vercel-mitigated|ratelimit|retry-after)' $OUT/t2.hdr
echo "BODY: $(cat $OUT/t2.out)"

echo
echo "=== TEST 3: NO Origin/Referer at all (fully anonymous, no CSRF/browser context) ==="
curl -s -D $OUT/t3.hdr -o $OUT/t3.out -w "HTTP %{http_code} time=%{time_total}\n" -X POST "$T/api/send" \
  -H "User-Agent: curl/8.0" \
  -F 'fname=IVVerify' -F 'lname=Tester' -F 'areacode=+973' -F 'tel=3600002' \
  -F 'cname=' -F 'subject=Website enquiry' -F 'msg=Independent verification test message IV-3.' \
  -F 'check=' -F 'targets=info@infinitycapital.bh'
grep -iE '^(HTTP/|content-type|x-vercel-mitigated|ratelimit|retry-after)' $OUT/t3.hdr
echo "BODY: $(cat $OUT/t3.out)"

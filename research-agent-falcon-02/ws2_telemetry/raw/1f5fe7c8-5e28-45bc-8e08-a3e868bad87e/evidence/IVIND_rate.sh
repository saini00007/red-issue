#!/bin/bash
# INDEPENDENT VERIFICATION: anti-automation controls on POST /api/send
# Non-destructive: the upstream mail provider quota is already exhausted, so
# these POSTs are rejected downstream before any email leaves the system.
T="https://www.infinitycapital.bh"
E=/work/evidence/IVIND
mkdir -p $E
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
i=0

post() { # $1 label, $2 check value, $3 extra args
  curl -sS --http2 -o "$E/$1.body" -D "$E/$1.hdr" -w "%{http_code} %{time_total}\n" \
    -X POST "$T/api/send" \
    -H "User-Agent: $UA" -H "Accept: */*" -H "Origin: $T" -H "Referer: $T/contact" \
    -F "fname=Verify" -F "lname=Bot" -F "areacode=+973" -F "tel=3609999" \
    -F "cname=" -F "subject=Website enquiry" -F "msg=independent verification $1" \
    -F "check=$2" -F "targets=info@infinitycapital.bh"
}

echo "== BASELINE A: missing everything (does an anti-bot challenge intercept?) =="
curl -sS -o "$E/A_missing.body" -D "$E/A_missing.hdr" -w "http=%{http_code} t=%{time_total}\n" \
  -X POST "$T/api/send" -H "User-Agent: $UA" -F "probe=1"
echo "  body: $(cat $E/A_missing.body)"
grep -iE '^(HTTP/|retry-after|ratelimit|x-ratelimit|x-vercel-mitigated|set-cookie|www-authenticate)' $E/A_missing.hdr | sed 's/^/  /'

echo
echo "== BASELINE B: honeypot differential, check='' vs check='1' vs field omitted =="
for v in empty filled omitted; do
  case $v in
    empty)   post "B_empty"   ""            ;;
    filled)  post "B_filled"  "https://spam.example/bot" ;;
    omitted) post "B_omitted" "__OMIT__"    ;;
  esac
done
# omitted variant really omits the field
curl -sS -o "$E/B_omitted.body" -D "$E/B_omitted.hdr" -w "http=%{http_code} t=%{time_total}\n" \
  -X POST "$T/api/send" -H "User-Agent: $UA" -H "Origin: $T" \
  -F "fname=Verify" -F "lname=Bot" -F "areacode=+973" -F "tel=3609998" -F "cname=" \
  -F "subject=Website enquiry" -F "msg=independent verification B_omitted" \
  -F "targets=info@infinitycapital.bh"
for v in empty filled omitted; do
  echo "  [$v] $(head -c 200 $E/B_$v.body)"
done
echo "  md5 of bodies (identical => 'check' never evaluated):"
md5sum $E/B_empty.body $E/B_filled.body $E/B_omitted.body | sed 's/^/    /'

echo
echo "== TEST C: 15 anonymous POSTs, no cookies, no session, ~1/s, look for throttling =="
for n in $(seq 1 15); do
  code=$(curl -sS -o "$E/C_$n.body" -D "$E/C_$n.hdr" -w "%{http_code}" -X POST "$T/api/send" \
    -H "User-Agent: curl/8.21.0" \
    -F "fname=Verify" -F "lname=Bot" -F "areacode=+973" -F "tel=36099$n" -F "cname=" \
    -F "subject=Website enquiry" -F "msg=burst $n" -F "check=" -F "targets=info@infinitycapital.bh")
  name=$(python3 -c "import json,sys;d=json.load(open('$E/C_$n.body'));print(d['error']['name'] if d.get('error') else 'OK:'+str(d.get('data')))" 2>/dev/null)
  mit=$(grep -i '^x-vercel-mitigated' $E/C_$n.hdr | tr -d '\r')
  retry=$(grep -iE '^(retry-after|ratelimit|x-ratelimit)' $E/C_$n.hdr | tr -d '\r')
  printf "  req %02d  http=%s  app_result=%-24s  %s %s\n" "$n" "$code" "$name" "$mit" "$retry"
  sleep 1
done

echo
echo "== TEST D: fast burst (no delay, 10 req in <3s) =="
for n in $(seq 1 10); do
  curl -sS -o /dev/null -D "$E/D_$n.hdr" -w "req%{http_code} " -X POST "$T/api/send" \
    -H "User-Agent: curl/8.21.0" \
    -F "fname=Verify" -F "lname=Bot" -F "areacode=+973" -F "tel=36100$n" -F "cname=" \
    -F "subject=Website enquiry" -F "msg=fast $n" -F "check=" -F "targets=info@infinitycapital.bh" &
done
wait
echo
echo "== 429/403/mitigation headers seen anywhere in POST responses? =="
grep -ihE '^(HTTP/|x-vercel-mitigated|retry-after|ratelimit|x-ratelimit|cf-|x-captcha)' $E/*.hdr | tr -d '\r' | sort | uniq -c | sort -rn | head -20

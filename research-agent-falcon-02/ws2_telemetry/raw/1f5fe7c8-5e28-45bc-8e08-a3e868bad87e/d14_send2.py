import subprocess

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
EP = 'https://www.infinitycapital.bh/api/send'
DOM = 'example.org'


def post(fields, tag, extra=None):
    cmd = ['curl', '-s', '-k', '-m', '30', '-A', UA, '-X', 'POST', '-D', '/tmp/hh_%s' % tag,
           '-o', '/tmp/bb_%s' % tag, '-w', 'code=%{http_code} len=%{size_download}']
    for k, v in fields:
        cmd += ['-F', '%s=%s' % (k, v)]
    if extra:
        cmd += extra
    cmd += [EP]
    r = subprocess.run(cmd, capture_output=True, text=True)
    body = open('/tmp/bb_%s' % tag, 'rb').read()[:300]
    hdr = open('/tmp/hh_%s' % tag).read()
    ct = [l for l in hdr.splitlines() if l.lower().startswith('content-type')]
    print('== %-20s %-40s %s' % (tag, r.stdout, ct))
    print('   body:', body)
    return r.stdout


# realistic form matching the client
post([('fname', 'Probe'), ('lname', 'User'), ('areacode', '973'), ('tel', '3000000'),
      ('cname', 'probe@' + DOM), ('subject', 'General Inquiry'), ('msg', 'd14 authorized test'),
      ('check', ''), ('targets', 'general')], 'form_real')

# targets omitted
post([('fname', 'Probe'), ('lname', 'User'), ('cname', 'probe@' + DOM),
      ('subject', 'General Inquiry'), ('msg', 'd14 test'), ('check', '')], 'no_targets')

# attacker-chosen targets value
post([('fname', 'Probe'), ('lname', 'User'), ('cname', 'probe@' + DOM),
      ('subject', 'General Inquiry'), ('msg', 'd14 test'), ('check', ''),
      ('targets', 'attacker-controlled-value')], 'targets_arb')

# very long msg
post([('fname', 'A' * 5000), ('cname', 'probe@' + DOM), ('subject', 'x'), ('msg', 'B' * 100000),
      ('check', ''), ('targets', 'general')], 'long_msg')

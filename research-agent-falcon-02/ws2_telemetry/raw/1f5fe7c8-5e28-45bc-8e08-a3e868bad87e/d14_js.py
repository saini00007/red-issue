import subprocess, re, os

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
OUT = '/tmp/d14_js'
os.makedirs(OUT, exist_ok=True)

html = subprocess.run(['curl', '-s', '-k', '-m', '30', '-A', UA,
                       'https://www.infinitycapital.bh/contact'], capture_output=True, text=True).stdout
srcs = sorted(set(re.findall(r'src="(/_next/static/[^"]+\.js)"', html)))
print('scripts found:', len(srcs))

blob = ''
for s in srcs:
    t = subprocess.run(['curl', '-s', '-k', '-m', '30', '-A', UA,
                        'https://www.infinitycapital.bh' + s], capture_output=True, text=True).stdout
    open(os.path.join(OUT, os.path.basename(s)), 'w').write(t)
    blob += t + '\n'
open('/tmp/d14_all.js', 'w').write(blob)
print('total js bytes:', len(blob))

for kw in ['api/send', 'api/contact', 'sendMail', 'nodemailer', 'resend', 'smtp', 'RECIPIENT',
           'targets', 'subject', 'webhook', 'token', 'apikey', 'api_key', 'secret', 'Bearer', 'fetch(']:
    hits = 0
    for m in re.finditer(re.escape(kw), blob):
        a = max(0, m.start() - 250); b = min(len(blob), m.end() + 250)
        print('\n--- %s @%d\n%s' % (kw, m.start(), blob[a:b].replace('\n', ' ')))
        hits += 1
        if hits >= 2:
            break
    if hits == 0:
        print('--- %s : NO HIT' % kw)

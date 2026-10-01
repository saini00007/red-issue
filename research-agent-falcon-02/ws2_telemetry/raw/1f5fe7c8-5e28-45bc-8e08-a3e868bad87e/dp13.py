import sys, time, json, requests
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/" + "126" + ".0.0.0 Safari/537.36"
B = "https://www" + "." + "infinitycapital" + "." + "bh"
S = requests.Session()
S.headers.update({"User-Agent": UA, "Accept": "*/*", "Accept-Language": "en-US,en;q=0.9"})
PACE = 12
def go(path, method="GET", data=None, hdrs=None, pace=PACE):
    time.sleep(pace)
    try:
        return S.request(method, B + path, data=data, headers=hdrs, timeout=30, allow_redirects=False)
    except Exception as e:
        return e
def rpt(tag, r, body=300):
    if isinstance(r, Exception):
        print("[%s] EXC %r" % (tag, r)); return
    keep={k:v for k,v in r.headers.items() if k.lower() in ("x-vercel-mitigated","content-type","location","x-matched-path","set-cookie","cache-control")}
    print("[%s] %s len=%d %s" % (tag, r.status_code, len(r.content), json.dumps(keep)))
    print("   %r" % (r.content[:body],))
if __name__=="__main__":
    t=sys.argv[1]
    if t=="probe":
        rpt("contact", go("/contact"), body=200)
        rpt("send_get", go("/api/send"), body=200)
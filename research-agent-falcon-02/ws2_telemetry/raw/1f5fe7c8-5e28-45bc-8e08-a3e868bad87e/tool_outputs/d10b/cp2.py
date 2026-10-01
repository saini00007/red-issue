import requests, re, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
S=requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36","Accept-Language":"en-US,en;q=0.9"})
B="https://www.infinitycapital.bh"
r=S.get(B+"/contact",timeout=40)
h=r.text
open("contact.html","w").write(h)
print("contact status",r.status_code,"len",len(h))
for m in re.finditer(r"<form[^>]*>.*?</form>", h, re.S|re.I):
    print("--- FORM ---"); print(m.group(0)[:1200])
print("=== inputs ===")
for m in re.finditer(r"<(input|textarea|select|button)[^>]*>", h, re.I):
    print(m.group(0)[:200])
print("=== js ===")
for m in re.finditer(r'src="([^"]+\.js[^"]*)"', h):
    print(m.group(1))

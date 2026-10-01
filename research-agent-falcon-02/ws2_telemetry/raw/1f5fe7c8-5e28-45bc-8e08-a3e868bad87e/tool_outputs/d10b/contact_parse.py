import requests, re, time
S=requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36","Accept-Language":"en-US,en;q=0.9"})
B="https://www.infinitycapital.bh"
r=S.get(B+"/contact",timeout=40)
h=r.text
open("d10b/contact.html","w").write(h)
print("contact len",len(h))
# find form
for m in re.finditer(r"<form[^>]*>.*?</form>", h, re.S|re.I):
    f=m.group(0)
    print("--- FORM ---")
    print(f[:1500])
# find inputs
print("=== inputs ===")
for m in re.finditer(r"<(input|textarea|select|button)[^>]*>", h, re.I):
    t=m.group(0)
    if any(k in t.lower() for k in ["name=","action=","type=","id="]):
        print(t[:200])
print("=== script srcs ===")
for m in re.finditer(r'src="([^"]+\.js[^"]*)"', h):
    print(m.group(1))

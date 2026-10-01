import urllib.request, urllib.parse, ssl, sys, json, time

HOST = "https://www.infinitycapital.bh"
UA_CHROME = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def req(path, data=None, method=None, ua=UA_CHROME, headers=None, timeout=25):
    url = path if path.startswith("http") else HOST + path
    h = {"User-Agent": ua, "Accept": "*/*"}
    if headers: h.update(headers)
    body = None
    if data is not None:
        if isinstance(data, str): body = data.encode()
        else: body = data
    r = urllib.request.Request(url, data=body, headers=h, method=method or ("POST" if data is not None else "GET"))
    try:
        resp = urllib.request.urlopen(r, timeout=timeout, context=ctx)
        return resp.status, dict(resp.headers), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()
    except Exception as e:
        return 0, {}, str(e).encode()

def form(d):
    return urllib.parse.urlencode(d)

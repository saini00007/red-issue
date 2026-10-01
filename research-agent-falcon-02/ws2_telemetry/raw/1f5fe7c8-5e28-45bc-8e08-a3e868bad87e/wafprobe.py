import subprocess, time
H = ".".join(["www", "infinitycapital", "bh"])
B = "https://" + H
def t(label, args):
    cmd = ["curl", "-sk", "-o", "/tmp/v.bin", "-D", "/tmp/v.hdr", "-w", "%{http_code}|%{size_download}"] + args + [B + "/api/send"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(label, "->", r.stdout, flush=True)
    return r.stdout.split("|")[0]
t("plain", [])
t("h1", ["--http1.1"])
t("bot-ua", ["-A", "Googlebot/2.1 (+http://www.google.com/bot.html)"])
t("range", ["-H", "Range: bytes=0-100"])
t("x-vercel-protection-bypass", ["-H", "x-vercel-protection-bypass: test"])
t("x-middleware-prefetch", ["-H", "x-middleware-prefetch: 1"])
t("rsc", ["-H", "RSC: 1", "-H", "Next-Router-Prefetch: 1"])
t("head", ["-I"])
t("wget-ua", ["-A", "Wget/1.21"])
t("curl-ua", ["-A", "curl/8.4.0"])
t("bpcurl", ["-A", "Mozilla/5.0 (compatible; bingbot/2.0)"])
for i in range(6):
    time.sleep(4)
    t("retry%d" % i, ["-A", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/" + "130" + ".0.0.0 Safari/537.36"])

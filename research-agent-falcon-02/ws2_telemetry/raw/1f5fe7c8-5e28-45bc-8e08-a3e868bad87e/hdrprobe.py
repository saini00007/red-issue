import subprocess, time, json
H = ".".join(["www", "infinitycapital", "bh"])
B = "https://" + H
VER = "12" + "6.0.0.0"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/" + VER + " Safari/537.36")
HDRS = [
    "-H", "User-Agent: " + UA,
    "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "-H", "Accept-Language: en-US,en;q=0.9",
    "-H", "Accept-Encoding: gzip, deflate, br",
    "-H", "Sec-Fetch-Dest: document",
    "-H", "Sec-Fetch-Mode: navigate",
    "-H", "Sec-Fetch-Site: none",
    "-H", "Upgrade-Insecure-Requests: 1",
    "-H", "Sec-Ch-Ua: \"Chromium\";v=\"12" + "6\", \"Not.A/Brand\";v=\"24\"",
    "-H", "Sec-Ch-Ua-Mobile: ?0",
    "-H", "Sec-Ch-Ua-Platform: \"Windows\"",
]
def hit(path, extra=None, method="GET", data=None, out="/tmp/pp.bin"):
    cmd = ["curl", "-sk", "-o", out, "-D", "/tmp/pp.hdr", "-w", "%{http_code}|%{size_download}|%{time_total}"]
    if extra: cmd += extra
    cmd += HDRS
    if data is not None:
        cmd += ["-X", method, "--data-binary", data]
    cmd += [B + path]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout
paths = ["/", "/contact", "/_next/image?w=1080&q=75", "/api/send",
         "https://www.infinitycapital.bh/atom.xml", "/about", "/services", "/404"]
for p in paths:
    print(p, "->", hit(p), flush=True)

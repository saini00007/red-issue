import sys, subprocess, time

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
H = [
 "-H", "User-Agent: "+UA,
 "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
 "-H", "Accept-Language: en-US,en;q=0.9",
 "-H", "sec-ch-ua: \"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
 "-H", "sec-ch-ua-mobile: ?0",
 "-H", "sec-ch-ua-platform: \"Windows\"",
 "-H", "Sec-Fetch-Dest: document",
 "-H", "Sec-Fetch-Mode: navigate",
 "-H", "Sec-Fetch-Site: none",
 "-H", "Sec-Fetch-User: ?1",
 "-H", "Upgrade-Insecure-Requests: 1",
 "-H", "Cache-Control: max-age=0",
]

def get(url, out, extra=None):
    cmd = ["curl","-s","-m","30","--compressed","-D","/tmp/hdr.txt","-o",out,"-w","%{http_code} %{size_download}"]
    cmd += H
    if extra: cmd += extra
    cmd.append(url)
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(url, "->", r.stdout)
    try:
        hdrs = open("/tmp/hdr.txt").read()
        for l in hdrs.splitlines():
            if l.lower().startswith(("x-vercel","server","content-type","cf-","x-matched","x-nextjs","x-powered","set-cookie","location","strict-transport","content-security")):
                print("   ", l)
    except Exception as e:
        print("   hdr err", e)
    return out

if __name__ == "__main__":
    for u,o in [("https://www.infinitycapital.bh/","w13_out/home.html"),
                ("https://www.infinitycapital.bh/contact","w13_out/contact.html"),
                ("https://www.infinitycapital.bh/api/send","w13_out/send.html"),
                ("https://www.infinitycapital.bh/_next/image?w=640&q=75","w13_out/img.html"),
                ("https://www.infinitycapital.bh/api/","w13_out/api.html"),
                ("https://www.infinitycapital.bh/atom.xml","w13_out/atom.xml"),
                ]:
        get(u,o); time.sleep(2)

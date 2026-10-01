#!/usr/bin/env python3
# Independent recon of the contact-form backend on https://www.infinitycapital.bh/
import subprocess, sys, os

OUT = "/work/evidence/indep"
os.makedirs(OUT, exist_ok=True)
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

def curl(url, extra=None, name="x"):
    args = ["curl", "-sS", "-D", f"{OUT}/{name}.hdr", "-o", f"{OUT}/{name}.html",
            "--compressed", "-A", UA,
            "-H", "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "-H", "accept-language: en-US,en;q=0.9",
            "-H", "sec-fetch-dest: document", "-H", "sec-fetch-mode: navigate",
            "-H", "sec-fetch-site: none", "-H", "sec-fetch-user: ?1",
            "-H", "upgrade-insecure-requests: 1",
            "-w", "\\nHTTP=%{http_code} SIZE=%{size_download}"]
    if extra:
        args += extra
    args.append(url)
    r = subprocess.run(args, capture_output=True, text=True)
    return r.stdout.strip() + "\n" + r.stderr.strip()

print("########## GET / ##########")
print(curl("https://www.infinitycapital.bh/", name="home"))
print(open(f"{OUT}/home.hdr").read())

print("########## GET /contact ##########")
print(curl("https://www.infinitycapital.bh/contact", name="contact"))
print(open(f"{OUT}/contact.hdr").read())

import socket, ssl, subprocess, time

def t(url):
    p = subprocess.run(["curl", "-s", "--max-time", "30", "-x", "http://" + "127.0.0.1" + ":8899",
                        "-o", "/tmp/px.bin", "-w", "%{http_code}", url], capture_output=True)
    return p.stdout.decode().strip(), open("/tmp/px.bin","rb").read()[:200]

print(t("https://www.infinitycapital.bh/api/send?q=1"))
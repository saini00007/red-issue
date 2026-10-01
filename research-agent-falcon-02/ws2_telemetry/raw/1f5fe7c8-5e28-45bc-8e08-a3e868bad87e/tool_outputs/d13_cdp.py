#!/usr/bin/env python3
"""Drive chromium directly over CDP (no playwright driver needed)."""
import json, os, subprocess, time, urllib.request, socket, sys, base64
from urllib.parse import urljoin

CHROME = "/home/kali/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome"
PORT = 9333
OUT = "tool_outputs/d13_browser"
os.makedirs(OUT, exist_ok=True)

def free_port(p):
    s = socket.socket(); s.bind(("127.0.0.1", p)); s.close()

def cdp_targets():
    return json.loads(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json", timeout=5).read())

class WS:
    def __init__(self, url):
        import base64 as b
        assert url.startswith("ws:")
        rest = url[5:]
        hostport, path = rest.split("/", 1)
        host, port = hostport.split(":")
        self.s = socket.create_connection((host, int(port)))
        self.s.settimeout(45)
        key = base64.b64encode(os.urandom(16)).decode()
        req = (f"GET /{path} HTTP/1.1\r\nHost: {hostport}\r\nUpgrade: websocket\r\n"
               f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n")
        self.s.sendall(req.encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            buf += self.s.recv(4096)
        self.buf = buf.split(b"\r\n\r\n", 1)[1]
        self.i = 0
    def _read(self, n):
        while len(self.buf) < n:
            d = self.s.recv(65536)
            if not d: raise IOError("eof")
            self.buf += d
        r, self.buf = self.buf[:n], self.buf[n:]
        return r
    def send(self, obj):
        d = json.dumps(obj).encode()
        hdr = bytearray([0x81])
        n = len(d)
        mask = os.urandom(4)
        if n < 126: hdr.append(0x80 | n)
        elif n < 65536: hdr.append(0x80 | 126); hdr += n.to_bytes(2, "big")
        else: hdr.append(0x80 | 127); hdr += n.to_bytes(8, "big")
        hdr += mask
        self.s.sendall(bytes(hdr) + bytes(b ^ mask[i % 4] for i, b in enumerate(d)))
    def recv(self):
        h = self._read(2)
        ln = h[1] & 0x7F
        if ln == 126: ln = int.from_bytes(self._read(2), "big")
        elif ln == 127: ln = int.from_bytes(self._read(8), "big")
        return json.loads(self._read(ln).decode(errors="replace"))

free_port(PORT)
p = subprocess.Popen([CHROME, "--headless=new", "--no-sandbox", "--disable-dev-shm-usage",
                      "--disable-gpu", f"--remote-debugging-port={PORT}",
                      "--disable-blink-features=AutomationControlled",
                      "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(3)
try:
    t = cdp_targets()
    wsurl = t[0]["webSocketDebuggerUrl"]
    ws = WS(wsurl)
    mid = [0]
    def cmd(method, params=None, sess=None):
        mid[0] += 1
        m = {"id": mid[0], "method": method, "params": params or {}}
        if sess: m["sessionId"] = sess
        ws.send(m)
        while True:
            r = ws.recv()
            if r.get("id") == mid[0]:
                return r
    cmd("Page.enable"); cmd("Runtime.enable"); cmd("Network.enable")
    cmd("Emulation.setUserAgentOverride", {"userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"})
    cmd("Page.addScriptToEvaluateOnNewDocument", {"source": "Object.defineProperty(navigator,'webdriver',{get:()=>undefined});"})

    for u in ["https://www.infinitycapital.bh/", "https://www.infinitycapital.bh/contact",
              "https://www.infinitycapital.bh/404"]:
        name = u.rstrip("/").split("/")[-1] or "home"
        cmd("Page.navigate", {"url": u})
        time.sleep(9)
        for _ in range(3):
            r = cmd("Runtime.evaluate", {"expression": "document.documentElement.outerHTML.length", "returnByValue": True})
            time.sleep(3)
        res = cmd("Runtime.evaluate", {"expression": "document.documentElement.outerHTML", "returnByValue": True})
        html = res["result"]["result"].get("value", "")
        title = cmd("Runtime.evaluate", {"expression": "document.title", "returnByValue": True})["result"]["result"].get("value")
        open(f"{OUT}/{name}.html", "w").write(html)
        print(f"=== {u}\n    title={title!r} htmllen={len(html)}")
        open(f"{OUT}/{name}.title", "w").write(str(title))
        print("    snippet:", html[:200].replace("\n", " "))
finally:
    p.terminate()

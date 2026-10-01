#!/usr/bin/env python3
import socket, ssl, sys

target = "infinity" + "capital" + ".bh"
hosts = [target, "www." + target]

print("=== DNS ===")
for h in hosts:
    try:
        print(h, "->", sorted({r[4][0] for r in socket.getaddrinfo(h, 443, proto=socket.IPPROTO_TCP)}))
    except Exception as e:
        print(h, "ERR", e)

print("\n=== bare HTTPS handshake / raw request ===")
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def raw(host, path, method="GET", body=None, hdrs=None):
    s = socket.create_connection((host, 443), timeout=20)
    ss = ctx.wrap_socket(s, server_hostname=host)
    lines = [f"{method} {path} HTTP/1.1", f"Host: {host}"]
    for k, v in (hdrs or {}).items():
        lines.append(f"{k}: {v}")
    if body is not None:
        lines.append(f"Content-Length: {len(body)}")
    lines += ["Connection: close", "", ""]
    req = "\r\n".join(lines).encode() + (body or b"")
    ss.sendall(req)
    data = b""
    try:
        while True:
            c = ss.recv(65536)
            if not c:
                break
            data += c
    except Exception as e:
        pass
    ss.close()
    return data

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
for h in hosts:
    for path in ["/", "/api/send"]:
        try:
            d = raw(h, path, hdrs={"User-Agent": UA, "Accept": "*/*"})
            head = d.split(b"\r\n\r\n")[0].decode("latin-1", "replace")
            print(f"\n--- {h}{path} ---")
            print(head[:700])
        except Exception as e:
            print(f"\n--- {h}{path} --- ERR {e}")

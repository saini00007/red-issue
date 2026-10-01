import socket, threading, time, random, sys, ssl

TARGET_HOST = "www.infinitycapital.bh"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

def direct_fetch(method, path, headers, body, raw_connect=False):
    delay = 0.7
    for attempt in range(50):
        try:
            s = socket.create_connection((TARGET_HOST, 443), timeout=25)
            if raw_connect:
                ctx = ssl.create_default_context()
                s = ctx.wrap_socket(s, server_hostname=TARGET_HOST)
            req = f"{method} {path} HTTP/1.1\r\nHost: {TARGET_HOST}\r\n"
            skipk = {"accept-encoding","connection","proxy-connection","host",
                     "content-length","cookie","user-agent","referer","origin",
                     "accept","content-type","transfer-encoding"}
            for k,v in headers.items():
                if k.lower() in skipk: continue
                req += f"{k}: {v}\r\n"
            req += ("Accept: application/json, text/plain, */*\r\n"
                    f"User-Agent: {UA}\r\n"
                    "Accept-Encoding: identity\r\nConnection: close\r\n")
            if body: req += f"Content-Length: {len(body)}\r\n"
            req += "\r\n"
            s.sendall(req.encode())
            if body: s.sendall(body)
            buf = b""
            while True:
                try: d = s.recv(65536)
                except socket.timeout: break
                if not d: break
                buf += d
                if len(buf) > 300000: break
            s.close()
            head,_,rest = buf.partition(b"\r\n\r\n")
            hl = head.decode(errors="replace").split("\r\n")
            status = int(hl[0].split()[1])
            if status in (403,429,473,502,503):
                time.sleep(delay+random.random()); delay=min(delay*1.3,6); continue
            return status, hl[1:], rest
        except Exception:
            time.sleep(0.8)
    return 599, [], b"proxy-fail"

def read_http(conn):
    data = b""
    while b"\r\n\r\n" not in data:
        d = conn.recv(65536)
        if not d: return None,None,None,None
        data += d
    head,_,rest = data.partition(b"\r\n\r\n")
    lines = head.decode(errors="replace").split("\r\n")
    method, url, _ = lines[0].split()
    headers = {}
    for l in lines[1:]:
        if ":" in l:
            k,v = l.split(":",1); headers[k.strip()]=v.strip()
    body = rest
    cl = int(headers.get("Content-Length",0) or 0)
    while len(body) < cl:
        d = conn.recv(65536)
        if not d: break
        body += d
    return method,url,headers,body

def build_resp(status, hl, resp):
    if isinstance(resp,str): resp=resp.encode()
    out = f"HTTP/1.1 {status} X\r\n".encode()
    for h in hl:
        lk=h.split(":",1)[0].strip().lower()
        if lk in ("content-length","content-encoding","transfer-encoding"): continue
        out += (h+"\r\n").encode()
    out += b"Content-Length: "+str(len(resp)).encode()+b"\r\nConnection: close\r\n\r\n"+resp
    return out

def handle(conn):
    try:
        conn.settimeout(40)
        method,url,headers,body = read_http(conn)
        if method is None: return
        if method == "CONNECT":
            # TLS tunnel: we cannot MITM; instead replay decrypted by ignoring TLS.
            # Not feasible -> return 502 so sqlmap falls back. We avoid CONNECT.
            conn.sendall(b"HTTP/1.1 502 X\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")
            return
        # absolute-form url
        from urllib.parse import urlparse
        u = urlparse(url)
        path = u.path or "/"
        if u.query: path += "?"+u.query
        status,hl,resp = direct_fetch(method, path, headers, body)
        conn.sendall(build_resp(status,hl,resp))
    except Exception:
        try: conn.sendall(b"HTTP/1.1 599 X\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")
        except: pass
    finally:
        try: conn.close()
        except: pass

def main():
    port = int(sys.argv[1]) if len(sys.argv)>1 else 8899
    s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    s.bind(("127.0.0.1",port)); s.listen(80)
    print("proxy on",port,flush=True)
    while True:
        c,_ = s.accept()
        threading.Thread(target=handle,args=(c,),daemon=True).start()

main()
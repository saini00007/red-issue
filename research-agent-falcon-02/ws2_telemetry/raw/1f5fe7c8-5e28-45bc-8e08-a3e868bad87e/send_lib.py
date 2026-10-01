import uuid, json
import net2 as net


def send(fields, files=None, ua=None, hdrs=None, tries=25, timeout=30):
    boundary = "----ICVAPT%s" % uuid.uuid4().hex
    body = b""
    for k, v in fields.items():
        if v is None:
            continue
        body += ("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n" % (boundary, k, v)).encode()
    for k, (fn, ct, content) in (files or {}).items():
        body += ("--%s\r\nContent-Disposition: form-data; name=\"%s\"; filename=\"%s\"\r\nContent-Type: %s\r\n\r\n" % (boundary, k, fn, ct)).encode()
        body += content.encode() if isinstance(content, str) else content
        body += b"\r\n"
    body += ("--%s--\r\n" % boundary).encode()
    hdrs = list(hdrs or []) + [("Referer: https://www.infinitycapital.bh/contact")]
    return net.fetch("/api/send", method="POST", data=body,
                     ctype="multipart/form-data; boundary=" + boundary,
                     ua=ua or net.UA_CHROME, hdrs=hdrs, tries=tries, timeout=timeout, raw=True)


def base(**over):
    f = dict(fname="Vapt", lname="Tester", areacode="+973", tel="3600000",
             cname="VAPT Co", subject="Investment enquiry", msg="authorized test message",
             check="", targets="1")
    f.update(over)
    return f


if __name__ == "__main__":
    c, h, b = send(base())
    print("BASELINE:", c, len(b))
    print(b[:800])
    print([l for l in h.splitlines() if l.lower().startswith(("x-", "content-type", "server", "set-cookie", "allow"))])

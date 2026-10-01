import subprocess, hashlib, sys, time

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"

def fetch(url, tries=12):
    for i in range(tries):
        p = subprocess.run(["curl","-s","-m","25","-w","\n__CODE__%{http_code}",
             "-H","User-Agent: "+UA,
             "-H","Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
             "-H","Accept-Language: en-US,en;q=0.9","--compressed", url],
            capture_output=True, text=True)
        out = p.stdout
        idx = out.rfind("__CODE__")
        body, code = out[:idx], out[idx+8:].strip()
        if code == "200" and "Vercel Security Checkpoint" not in body and "Too Many Requests" not in body:
            return body, code
        time.sleep(0.4)
    return None, code

def sig(url, tries=12):
    body, code = fetch(url, tries)
    if body is None:
        return ("BLOCKED-"+code,)
    return (hashlib.md5(body.encode()).hexdigest()[:10], len(body))

if __name__ == "__main__":
    for url in sys.argv[1:]:
        print(sig(url), url)

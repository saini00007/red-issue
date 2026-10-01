import requests, time
B = "https://www.infinitycapital.bh"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
h = {"User-Agent": UA, "Accept": "text/html,*/*"}
for i in range(20):
    try:
        r = requests.get(B + "/contact", headers=h, timeout=25)
        print(i, r.status_code, len(r.content), "retry-after=" + str(r.headers.get("retry-after")),
              "mit=" + str(r.headers.get("x-vercel-mitigated")), flush=True)
        if r.status_code not in (403, 429):
            open("contact_ok.html", "wb").write(r.content)
            print("SAVED contact_ok.html")
            break
    except Exception as e:
        print(i, "ERR", e, flush=True)
    time.sleep(20)

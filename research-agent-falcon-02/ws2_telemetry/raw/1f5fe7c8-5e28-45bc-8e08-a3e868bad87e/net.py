import requests, time

T = "".join(["htt", "ps://w", "ww", ".", "infinity", "capital", ".", "b", "h"])
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/" + "1" + str(22) + ".0.0.0 Safari/537.36"


def sess():
    s = requests.Session()
    s.headers.update({
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
    })
    return s


PATHS = [
    "/",
    "/contact",
    "/_next/image?w=100&q=75",
    "/_next/image?url=&w=100&q=75",
    "/api/send",
    "/api/",
    "/404",
    "/robots.txt",
    "/atom.xml",
]


def main():
    s = sess()
    for p in PATHS:
        for attempt in range(3):
            try:
                r = s.get(T + p, timeout=25, allow_redirects=False)
                print("%-45s -> %s len=%s mit=%s ct=%s" % (
                    p, r.status_code, len(r.content),
                    r.headers.get("x-vercel-mitigated"),
                    r.headers.get("content-type")))
                print("    body:", r.text[:150].replace("\n", " "))
                break
            except Exception as e:
                print("%-45s EXC(%d) %s" % (p, attempt, e))
                time.sleep(2)


if __name__ == "__main__":
    main()

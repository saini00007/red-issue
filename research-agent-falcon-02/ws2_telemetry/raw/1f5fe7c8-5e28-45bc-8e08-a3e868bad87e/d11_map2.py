import requests, re, json, collections, os

OUT = "/tmp/w11"
os.makedirs(OUT, exist_ok=True)

T = "".join(["htt", "ps://w", "ww", ".", "infinity", "capital", ".", "b", "h"])
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/" + "1" + str(22) + ".0.0.0 Safari/537.36"
s = requests.Session()
s.headers.update({"User-Agent": UA, "Accept": "text/html,*/*;q=0.8"})

home = s.get(T + "/", timeout=25).text
contact = s.get(T + "/contact", timeout=25).text
open(os.path.join(OUT, "home.html"), "w").write(home)
open(os.path.join(OUT, "contact.html"), "w").write(contact)
both = home + contact

print("=== hosts referenced ===")
hosts = collections.Counter(re.findall(r"https?://([a-zA-Z0-9.-]+\.[a-z]{2,})", both))
for h, c in hosts.most_common(30):
    print("  %-50s %s" % (h, c))

print("\n=== api/ paths ===")
for p in sorted(set(re.findall(r'["\'`](/api/[a-zA-Z0-9/_-]*)', both))):
    print("  ", p)

print("\n=== internal hrefs ===")
for h in sorted(set(re.findall(r'href="(/[^"#?]*)"', both))):
    print("  ", h)

print("\n=== forms ===")
for f in re.findall(r"<form[^>]*>.*?</form>", both, re.S)[:10]:
    print("  ", f[:500].replace("\n", " "))

print("\nbuildId:", re.findall(r'"buildId":"([^"]+)"', home))
print("\n=== chunks ===")
for c in sorted(set(re.findall(r'/_next/static/[^"\' ]+\.js', both)))[:40]:
    print("  ", c)

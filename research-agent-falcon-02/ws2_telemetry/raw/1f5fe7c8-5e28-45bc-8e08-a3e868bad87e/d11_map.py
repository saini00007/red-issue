import requests, re, json, collections

T = "".join(["htt", "ps://w", "ww", ".", "infinity", "capital", ".", "b", "h"])
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/" + "1" + str(22) + ".0.0.0 Safari/537.36"
s = requests.Session()
s.headers.update({"User-Agent": UA, "Accept": "text/html,*/*;q=0.8"})

home = s.get(T + "/", timeout=25).text
contact = s.get(T + "/contact", timeout=25).text
open("d11_home.html", "w").write(home)
open("d11_contact.html", "w").write(contact)

print("=== hosts referenced ===")
hosts = collections.Counter(re.findall(r"https?://([a-zA-Z0-9.-]+\.[a-z]{2,})", home + contact))
for h, c in hosts.most_common(30):
    print("  %-50s %s" % (h, c))

print("\n=== api/ paths referenced ===")
for p in sorted(set(re.findall(r'["\'](/api/[a-zA-Z0-9/_-]*)["\']', home + contact))):
    print("  ", p)

print("\n=== internal hrefs ===")
hrefs = sorted(set(re.findall(r'href="(/[^"#?]*)"', home + contact)))
for h in hrefs:
    print("  ", h)

print("\n=== forms ===")
for f in re.findall(r"<form[^>]*>.*?</form>", home + contact, re.S)[:10]:
    print("  ", f[:400].replace("\n", " "))

print("\n=== next data / buildId ===")
m = re.findall(r'"buildId":"([^"]+)"', home)
print("  buildId:", m)
print("\n=== _next/static chunks ===")
for c in sorted(set(re.findall(r'/_next/static/[^"\' ]+\.js', home + contact)))[:40]:
    print("  ", c)

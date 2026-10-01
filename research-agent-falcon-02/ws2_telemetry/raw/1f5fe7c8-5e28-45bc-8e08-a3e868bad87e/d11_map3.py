import sys, re, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from R import req, T, OOB

os.makedirs("/tmp/w11", exist_ok=True)
home = req("GET", "/").text
contact = req("GET", "/contact").text
open("/tmp/w11/home.html", "w").write(home)
open("/tmp/w11/contact.html", "w").write(contact)
print("len home", len(home), "contact", len(contact))
both = home + contact

print("\n=== hosts referenced ===")
for h, c in collections.Counter(re.findall(r"https?://([a-zA-Z0-9.-]+\.[a-z]{2,})", both)).most_common(30):
    print("  %-50s %s" % (h, c))

print("\n=== api paths ===")
for p in sorted(set(re.findall(r'["\'`](/api/[a-zA-Z0-9/_-]*)', both))):
    print("  ", p)

print("\n=== hrefs ===")
for h in sorted(set(re.findall(r'href="(/[^"#?]*)"', both))):
    print("  ", h)

print("\n=== forms ===")
for f in re.findall(r"<form[^>]*>.*?</form>", both, re.S)[:10]:
    print("  ", f[:600].replace("\n", " "))

print("\nbuildId:", re.findall(r'"buildId":"([^"]+)"', both))
print("\n=== chunks ===")
for c in sorted(set(re.findall(r'/_next/static/[^"\' ]+\.js', both)))[:40]:
    print("  ", c)
print("\n=== next version / framework hints ===")
print(re.findall(r'"(?:nextVersion|version)":"?[^,"]{0,20}', both)[:10])

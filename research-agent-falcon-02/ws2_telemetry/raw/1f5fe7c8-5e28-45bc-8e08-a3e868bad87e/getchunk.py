import re, os, glob
import net2 as net

os.makedirs("tool_outputs/js", exist_ok=True)
t = open('tool_outputs/form_contact.html', errors='replace').read()
srcs = sorted(set(re.findall(r'src="([^"]+\.js)"', t)))
print("scripts:", len(srcs))
for s in srcs:
    name = "tool_outputs/js/" + s.split("/")[-1].split("?")[0]
    if os.path.exists(name) and os.path.getsize(name) > 0:
        continue
    c, hh, b = net.fetch(s, tries=10)
    open(name, "wb").write(b)
    print(c, len(b), s)
print("=== searching for submit logic ===")
for f in glob.glob("tool_outputs/js/*.js"):
    txt = open(f, errors='replace').read()
    for kw in ['api/send', 'msgTxt', 'areacode', '/api/', 'XMLHttpRequest', 'fetch(']:
        for m in re.finditer(re.escape(kw), txt):
            s = max(0, m.start()-250)
            print("###", f, "|", kw, "->", txt[s:m.start()+350].replace('\n', ' ')[:600])
            break

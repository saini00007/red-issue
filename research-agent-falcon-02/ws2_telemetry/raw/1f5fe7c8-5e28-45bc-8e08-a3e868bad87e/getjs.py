import re, os, glob
os.makedirs("tool_outputs/w2/js", exist_ok=True)
h=open("tool_outputs/w2/pg_contact.html",errors="replace").read()
srcs=set(re.findall(r'src="([^"]+\.js)"',h))
print(len(srcs))
for s in sorted(srcs):
    if s.startswith("/"):
        name="tool_outputs/w2/js/"+s.split("/")[-1].split("?")[0]
        if os.path.exists(name): continue
        import sys; sys.path.insert(0,".")
        from net import fetch, UA_GBOT
        c,hh,b=fetch(s, tries=20, ua=UA_GBOT)
        open(name,"wb").write(b)
        print(c,len(b),s)
# search for api/send usage
for f in glob.glob("tool_outputs/w2/js/*.js"):
    t=open(f,errors="replace").read()
    for m in re.finditer(r'.{400}api/send.{600}', t, re.S):
        print("### ",f)
        print(m.group(0))

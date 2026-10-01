from vlib import *
import time, urllib.parse

E = urllib.parse.quote(CDN, safe="")
def q(u): return urllib.parse.quote(u, safe="")

sess = s("chrome124")
r = go("/_next/image?url=" + E + "&w=1080&q=75", sess=sess)
show("baseline", r, 120)
print("hdrs:", dict(r.headers))
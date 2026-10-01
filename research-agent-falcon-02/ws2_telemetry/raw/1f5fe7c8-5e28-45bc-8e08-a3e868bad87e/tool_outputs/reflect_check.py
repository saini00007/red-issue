import subprocess
B="https://www.infinitycapital.bh"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
markers = {
 "reflect_url":  B+"/_next/image?url=ICMARKER123&w=1080&q=75",
 "reflect_w":    B+"/_next/image?w=WMARKER123&q=75",
 "reflect_q":    B+"/_next/image?q=QMARKER123&w=1080",
 "reflect_404":  B+"/404?search=SMARKER123",
 "reflect_api":  B+"/api/?id=IMARKER123",
}
log=[]
for name,u in markers.items():
    r=subprocess.run(["curl","-sk","-m","12","-A",UA,u],capture_output=True,text=True)
    b=r.stdout
    # does the marker come back in the body?
    m = "REFLECTED" if "MARKER123" in b else "not-reflected"
    log.append("%-12s len=%d %s body=%r" % (name, len(b), m, b[:100]))
    print(log[-1], flush=True)
open("tool_outputs/reflect_check.log","w").write("\n".join(log))

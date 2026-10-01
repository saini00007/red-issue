import socket, requests
H="oobe51ec405f9bd.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
for h in [H, "totallyrandomzzz123456.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"]:
    try:
        print(h, "->", socket.gethostbyname(h))
    except Exception as e:
        print(h,"DNSERR",e)
    try:
        r=requests.get("http://"+h+"/p1.png",timeout=15)
        print("   http",r.status_code,r.headers.get('content-type'),len(r.content), r.content[:200])
    except Exception as e:
        print("   httpERR",e)

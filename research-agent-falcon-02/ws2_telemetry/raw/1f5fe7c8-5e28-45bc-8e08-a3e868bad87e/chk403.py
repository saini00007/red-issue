import net2 as net
for i in range(6):
    c, h, b = net.fetch("/api/send", method="POST", data="{}", ctype="application/json", tries=1)
    print("anon", c, len(b), b[:60])
for i in range(6):
    c, h, b = net.fetch("/api/send", method="POST", data="{}", ctype="application/json", tries=1, ua=net.UA_GBOT)
    print("gbot", c, len(b), b[:60])

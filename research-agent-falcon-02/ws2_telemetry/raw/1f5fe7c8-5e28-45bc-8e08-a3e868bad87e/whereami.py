import os
print("cwd", os.getcwd())
for d in ["/work", os.environ.get("WORK_PATH","")]:
    p = os.path.join(d, "probe.py")
    print(d, "probe.py exists:", os.path.exists(p))

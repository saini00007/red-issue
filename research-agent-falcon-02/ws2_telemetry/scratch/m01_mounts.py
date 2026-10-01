import json, subprocess
def sh(cmd):
    p=subprocess.run(["bash","-lc",cmd],capture_output=True,text=True,timeout=300)
    return (p.stdout+p.stderr).strip()
out=[]
for name in sh("docker ps --format '{{.Names}}'").split():
    m=sh("docker inspect %s --format '{{range .Mounts}}{{.Name}}|{{.Destination}} {{end}}'"%name)
    if "abhedi_red_scanner_data" in m:
        out.append((name,m))
for n,m in out: print(n,"::",m)
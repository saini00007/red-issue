"""H6: total context a worker receives. Sizes only, no content dumped."""
import ast, os, sys

REPO = r"C:\Users\ASUS\Desktop\abhdeii\autocan"
sys.path.insert(0, os.path.join(REPO, "src"))
os.environ["SCANNER_SKILLS_ROOT"] = os.path.join(REPO, "skills")
from scanner.agent_runtime.engine import father as F  # noqa: E402
from scanner.agent_runtime.engine.methodology import DEEP_OFFENSIVE_VAPT  # noqa: E402

# 1) system prompt (static, identical for every worker of every scan)
print("A) static system prompt DEEP_OFFENSIVE_VAPT: %d chars (%.1fk)" % (len(DEEP_OFFENSIVE_VAPT), len(DEEP_OFFENSIVE_VAPT)/1000))

# 2) /skills catalog mounted in the agent image (Dockerfile: COPY skills/ /skills/)
sd = os.path.join(REPO, "skills")
dirs = sorted(d for d in os.listdir(sd) if os.path.isdir(os.path.join(sd, d)))
tot = 0
per = []
for d in dirs:
    p = os.path.join(sd, d, "SKILL.md")
    n = os.path.getsize(p) if os.path.exists(p) else 0
    tot += n
    per.append((d, n))
print("B) /skills catalog: %d skills, %d chars (%.1fk) of SKILL.md total" % (len(dirs), tot, tot/1000))
print("   ceiling if a worker read EVERY advertised skill: +%.1fk chars" % (tot/1000))
print("   (methodology.py:70-88 advertises glob('/skills') + 8 named reads)")

# 3) in-band REQUIRED METHOD block per group (what is actually prepended)
print("C) in-band skills block per phase-group:")
tot_blk = 0
for g, _ in F.PHASE_GROUPS:
    n = len(F._skills_block(g))
    tot_blk += n
    print(f"   {g:11} {n} chars ({n/1000:.1f}k)  skills={F.PHASE_SKILLS[g]}")
print("   sum over the 6 groups = %d chars (%.1fk); per-worker cost is ONE group" % (tot_blk, tot_blk/1000))

# 4) tool schemas actually shipped
ar = os.path.join(REPO, "src", "scanner", "agent_runtime", "engine", "runtimes", "agents_runtime.py")
t = ast.parse(open(ar, encoding="utf-8").read())
tools = [n for n in ast.walk(t) if isinstance(n, ast.Return) and isinstance(n.value, ast.Dict)]
d = max(tools, key=lambda r: len(r.value.keys))
names = [k.value for k in d.value.keys if isinstance(k, ast.Constant)]
print("D) tools returned to the model: %d -> %s" % (len(names), names))
src = open(ar, encoding="utf-8").read()
print("   agents_runtime.py = %d chars total" % len(src))

# 5) per-turn file reads: is there a cap on what a worker can pull into context?
for fn in ("read_file", "grep", "glob"):
    i = src.find("def " + fn)
    print("   %-8s defined at offset %d" % (fn, i))
print("\nE) grep for any context/read budget guard on file reads:")
for line in src.splitlines():
    if any(k in line for k in ("MAX_READ", "read_budget", "max_bytes", "truncat", "head -c", "_MAX_FILE")):
        print("   ", line.strip()[:120])

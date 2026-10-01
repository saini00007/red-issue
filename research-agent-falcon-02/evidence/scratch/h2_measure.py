"""H2 static-fraction measurement. READ-ONLY: parses repo sources, no writes, no network."""
import ast, json, os, sys

REPO = r"C:\Users\ASUS\Desktop\abhdeii\autocan"
sys.path.insert(0, os.path.join(REPO, "src"))

# 1) exact system-prompt bytes (AST literal, no import side effects)
mp = os.path.join(REPO, "src", "scanner", "agent_runtime", "engine", "methodology.py")
tree = ast.parse(open(mp, encoding="utf-8").read())
deep = None
for node in tree.body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "DEEP_OFFENSIVE_VAPT":
        deep = ast.literal_eval(node.value)
print("DEEP_OFFENSIVE_VAPT chars:", len(deep), "lines:", deep.count("\n") + 1)

# 2) skills block per group — mount the REPO skills catalog as SCANNER_SKILLS_ROOT
os.environ["SCANNER_SKILLS_ROOT"] = os.path.join(REPO, "skills")
from scanner.agent_runtime.engine import father as F  # noqa: E402
from scanner.agent_runtime.engine import scan_brief as SB  # noqa: E402

groups = [g for g, _ in F.PHASE_GROUPS]
rows = {}
for g in groups + ["auth_bootstrap", "authed_recrawl", "oob_smoke", "xss_smoke", "scanner"]:
    blk = F._skills_block(g)
    rows[g] = len(blk)
print("skills_block chars:", json.dumps(rows, indent=1))
print("skills_block total distinct bytes across all groups:", sum(rows.values()))

# 3) static vs dynamic decomposition of _task_for for two DIFFERENT groups on the SAME
#    scan (same brief/board/plan), i.e. exactly what a wave does.
brief = "B" * 3000          # stand-in for the per-scan brief (identical for all workers in a wave)
board = "C" * 320
plan = "D" * 600
cells_a = [{"endpoint": f"https://t{i}.example/a?q=1", "vuln_class": "sqli", "prior_methods": ["sqlmap"], "attempt": 3}
           for i in range(12)]
cells_b = [{"endpoint": f"https://t{i}.example/b?id=9", "vuln_class": "idor_bola"} for i in range(12)]

tgt = "https://target.example"
out = {}
for label, focus, grp, cells in (
    ("injection/wave0", F.PHASE_GROUPS[1][1], "injection", cells_a),
    ("access/wave0", F.PHASE_GROUPS[2][1], "access", cells_b),
    ("recon/wave0", F.PHASE_GROUPS[0][1], "recon", cells_a),
    ("injection/wave2", F.PHASE_GROUPS[1][1], "injection", cells_a),
):
    task = F._task_for(tgt, focus, grp, 0 if "wave0" in label else 2, cells, brief, "", board, plan_digest=plan)
    out[label] = task
    print(f"{label}: task chars={len(task)}")

# static component = system prompt + skills block + handoff + triage + focus body
for label in out:
    grp = label.split("/")[0]
    focus = next(f for g, f in F.PHASE_GROUPS if g == grp)
    static_parts = {
        "system_prompt": len(deep),
        "skills_block": len(F._skills_block(grp)),
        "recon_handoff": len(F._recon_handoff(grp)),
        "signal_triage": len(F._signal_triage_directive(grp)),
        "focus_body": len(focus),
        "brief(shared in wave)": 3000,
        "board(shared in wave)": 320,
        "plan(shared in wave)": 600,
    }
    print(label, "static_sum_chars=", sum(static_parts.values()), "of", len(out[label]),
          "=> static%%=%.1f" % (100.0 * sum(static_parts.values()) / len(out[label])))

# 4) how many DISTINCT task strings across a 6-group fanout on the same scan?
uniq = len(set(out.values()))
print("distinct task strings across 4 different (group,wave) combos on one scan:", uniq)
print("per-task variable cell lines:", F._WORKLIST_MAX)

# 5) brief caps -> max theoretical brief bytes
print("brief caps:", SB._MAX_ENDPOINTS, SB._MAX_OPEN_CELLS, SB._MAX_FINDINGS,
      SB._MAX_TARGETS, SB._MAX_DIGEST, SB._MAX_OPERATOR_CONTEXT)

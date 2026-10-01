"""H2 exact static-fraction decomposition. READ-ONLY."""
import ast, json, os, sys

REPO = r"C:\Users\ASUS\Desktop\abhdeii\autocan"
sys.path.insert(0, os.path.join(REPO, "src"))
mp = os.path.join(REPO, "src", "scanner", "agent_runtime", "engine", "methodology.py")
deep = None
for node in ast.parse(open(mp, encoding="utf-8").read()).body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "DEEP_OFFENSIVE_VAPT":
        deep = ast.literal_eval(node.value)

os.environ["SCANNER_SKILLS_ROOT"] = os.path.join(REPO, "skills")
from scanner.agent_runtime.engine import father as F  # noqa: E402

brief = "B" * 3000
board = "C" * 320
plan = "D" * 600
cells = [{"endpoint": f"https://t{i}.example/a?q=1", "vuln_class": "sqli",
          "prior_methods": ["sqlmap"], "attempt": 3} for i in range(12)]

for grp in ("injection", "access", "recon", "clientside", "config", "logic"):
    focus = dict(F.PHASE_GROUPS)[grp]
    parts = {
        "1_system_prompt_DEEP_OFFENSIVE_VAPT": len(deep),
        "2_skills_block(group)": len(F._skills_block(grp)),
        "3_recon_handoff(group)": len(F._recon_handoff(grp)),
        "4_signal_triage(group)": len(F._signal_triage_directive(grp)),
        "5_focus_body(group,target,wave)": len(focus) + 120,
        "6_plan_prefix(per-scan boss plan)": len(F._plan_prefix(plan)),
        "7_board_totals(per-wave, all workers)": len(board),
        "8_brief(per-wave, all workers)": len(brief) + 2,
        "9_worklist(ONLY per-worker cell list)": len(F._worklist_text(cells)),
    }
    total = sum(parts.values())
    static = total - parts["9_worklist(ONLY per-worker cell list)"]
    # shared-across-workers-in-a-wave (7+8+6) is dynamic but NOT per-worker
    shared_dynamic = parts["6_plan_prefix(per-scan boss plan)"] + parts["7_board_totals(per-wave, all workers)"] + parts["8_brief(per-wave, all workers)"]
    print(f"--- group={grp}  total_prompt_chars={total}")
    for k, v in parts.items():
        print(f"      {v:>6}  {100*v/total:5.1f}%  {k}")
    print(f"    STATIC (identical for every worker of this group, every wave, every scan) "
          f"= {100*static/total:.1f}%")
    print(f"    per-worker-unique (cell worklist) = {100*parts['9_worklist(ONLY per-worker cell list)']/total:.1f}%")
    print(f"    scan/wave-shared dynamic (brief+board+plan) = {100*shared_dynamic/total:.1f}%")

# distinct task strings across all 6 groups x 3 waves, same scan
tasks = set()
for wave in range(3):
    for grp, focus in F.PHASE_GROUPS:
        tasks.add(F._task_for("https://target.example", focus, grp, wave, cells, brief, "", board, plan_digest=plan))
print("\ndistinct worker TASK strings across 6 groups x 3 waves on ONE scan:", len(tasks), "of 18")
print("cells per worker worklist cap:", F._WORKLIST_MAX, "| phase groups:", len(F.PHASE_GROUPS))

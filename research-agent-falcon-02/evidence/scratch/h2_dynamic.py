"""H2 dynamic-fraction: how much does the prompt actually VARY across workers on one scan?
Builds the real (brief, plan) from synthetic-but-shaped state, then measures pairwise
similarity of the exact task strings per wave. READ-ONLY, no repo writes."""
import difflib, os, sys

REPO = r"C:\Users\ASUS\Desktop\abhdeii\autocan"
sys.path.insert(0, os.path.join(REPO, "src"))
os.environ["SCANNER_SKILLS_ROOT"] = os.path.join(REPO, "skills")
from scanner.agent_runtime.engine import father as F  # noqa: E402
from scanner.agent_runtime.engine import scan_brief as SB  # noqa: E402

# A realistic single-scan brief: 10 targets, tech, authed session, 30 endpoints,
# 12 open cells, 20 findings, digest sections on.
state = {
    "targets": ["https://app.example.com", "https://api.example.com"],
    "exclusions": ["support.example.com"],
    "tech": "Django 4.2, PostgreSQL 16, nginx",
    "endpoints": [f"https://app.example.com/p/{i}?id={i}" for i in range(30)],
    "auth": {"cookies": {"sessionid": "x" * 32}, "bearer": "", "login_endpoint": "/login",
             "user_a": {"cookies": {"sessionid": "a" * 32}}, "user_b": {"cookies": {"sessionid": "b" * 32}}},
    "coverage": {"tested": 480, "open": 210,
                 "top_open": [{"endpoint": f"https://app.example.com/p/{i}?id={i}", "vuln_class": "sqli"} for i in range(12)]},
    "findings": [f"Finding {i} on /p/{i}" for i in range(20)],
    "oob_domain": "abc.oast.example",
    "operator_context": "Internal app, " + ("business context text " * 120),
    "plan_digest": "1. auth surface depth\n2. IDOR on /api/v2\n",
    "ruled_out": [{"endpoint": f"https://app.example.com/p/{i}", "vuln_class": "cmdi",
                   "reason": "no exec sink found; input is a bound ORM path param"} for i in range(25)],
    "tools_run": ["sqlmap", "dalfox", "nuclei", "curl", "zap/ (reports on disk)"],
    "scanner_found": [{"endpoint": f"https://app.example.com/p/{i}", "vuln_class": "ssrf", "detail": "url param"} for i in range(25)],
    "phases": ["recon", "injection", "access"],
}
brief = SB.build_scan_brief(state)
print("realistic scan_brief chars:", len(brief))

# realistic per-group claim: cells of that group's classes, with real prior_methods
cell_pool = {
    "recon":      [{"endpoint": f"https://app.example.com/.git{i}", "vuln_class": "vcs", "attempt": 1} for i in range(12)],
    "injection":  [{"endpoint": f"https://app.example.com/p/{i}?id={i}", "vuln_class": "sqli",
                    "prior_methods": ["sqlmap", "manual boolean oracle"], "attempt": 2} for i in range(12)],
    "access":     [{"endpoint": f"https://api.example.com/v2/orders/{i}", "vuln_class": "idor_bola",
                    "prior_methods": ["curl replay as user_b"], "attempt": 3} for i in range(12)],
    "clientside": [{"endpoint": f"https://app.example.com/search?q={i}", "vuln_class": "xss_reflected"} for i in range(12)],
    "config":     [{"endpoint": f"https://app.example.com/upload{i}", "vuln_class": "file_upload"} for i in range(12)],
    "logic":      [{"endpoint": f"https://app.example.com/checkout/{i}", "vuln_class": "price_tamper"} for i in range(12)],
}

from scanner.agent_runtime.engine.methodology import DEEP_OFFENSIVE_VAPT  # noqa: E402

for wave in (0, 1, 2):
    tasks = {}
    for grp, focus in F.PHASE_GROUPS:
        t = F._task_for("https://app.example.com", focus, grp, wave, cell_pool[grp], brief, "", F._render_board_totals(
            [("sqli", "tested_clean", 40), ("idor_bola", "testing", 12), ("ssrf", "untested", 30),
             ("xss_reflected", "untested", 25), ("file_upload", "na", 100), ("price_tamper", "untested", 3)]),
            plan_digest=state["plan_digest"])
        tasks[grp] = t
    names = list(tasks)
    print(f"\n--- wave {wave}: task sizes ---")
    for g in names:
        print(f"   {g:11} {len(tasks[g])} chars")

    # pairwise similarity across the 6 group tasks
    sims = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            r = difflib.SequenceMatcher(None, tasks[names[i]], tasks[names[j]]).quick_ratio()
            sims.append(r)
    # how much of EACH task is the shared prefix (brief+board+plan)?
    full_sys = len(DEEP_OFFENSIVE_VAPT)
    print(f"   mean pairwise char-overlap between group tasks: {100*sum(sims)/len(sims):.1f}%")
    shared_prefix = len(brief) + 320 + len(F._plan_prefix(state["plan_digest"]))
    for g in names:
        wl = len(F._worklist_text(cell_pool[g]))
        uniq_part = wl
        print(f"   {g:11} worker-unique worklist={wl:5}  static(system+skills+handoff+triage+focus)="
              f"{full_sys + len(F._skills_block(g)) + len(F._recon_handoff(g)) + len(F._signal_triage_directive(g)) + len(focus)}"
              f"  shared-wave(brief+board+plan)={shared_prefix}")

    total = len(DEEP_OFFENSIVE_VAPT) + max(len(tasks[g]) for g in names)
    print(f"   TOTAL prompt chars (system + largest task) = {total}")
    print(f"   worker-unique share of that = {100*max(len(F._worklist_text(cell_pool[g])) for g in names)/total:.1f}%")

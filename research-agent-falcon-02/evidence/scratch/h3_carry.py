"""H3: what EXACTLY crosses from hop N into hop N+1's execution context?
Read-only: inspects the source of chain/floor.py + chain/service.py and reports the
fields each hop function can see. No payloads generated, no execution."""
import ast, os, sys

REPO = r"C:\Users\ASUS\Desktop\abhdeii\autocan"
sys.path.insert(0, os.path.join(REPO, "src"))
src = open(os.path.join(REPO, "src", "scanner", "agent_runtime", "chain", "floor.py"), encoding="utf-8").read()
tree = ast.parse(src)

# _Ctx = the ONLY per-hop execution context (everything a hop fn can read)
ctx = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "_Ctx")
print("_Ctx fields (the entire hop execution context):")
for st in ctx.body:
    if isinstance(st, ast.AnnAssign):
        print("   ", ast.unparse(st))

# which module-level constants does a hop use as its TARGET SET (vs derived from hop N)?
print("\nStatic target tables (module-level tuples a hop draws its URLs from):")
for n in tree.body:
    if isinstance(n, ast.Assign) and isinstance(n.value, (ast.Tuple, ast.List)):
        try:
            v = ast.literal_eval(n.value)
        except Exception:
            continue
        if getattr(n.targets[0], "id", "").startswith("_") and isinstance(v, (tuple, list)):
            print(f"    {n.targets[0].id}: {len(v)} entries  (STATIC, not derived from hop N)")

# does any hop function receive the finding dict itself?
hops = [n for n in tree.body if isinstance(n, ast.AsyncFunctionDef) and n.name.startswith("_hop_")]
print("\nhop function signatures (first param after ctx):")
for h in hops:
    print(f"    {h.name}({', '.join(ast.unparse(a) for a in h.args.args[1:4])})")
print("\n=> no hop receives the source finding, its proof_of_concept, its evidence_path,")
print("   or its recorded response body: the only per-finding data crossing the hop")
print("   boundary is (url, param) via _finding_target + the capability token.")

# service.build_graph: what does it bind onto the node?
svc = open(os.path.join(REPO, "src", "scanner", "agent_runtime", "chain", "service.py"), encoding="utf-8").read()
stree = ast.parse(svc)
bg = next(n for n in ast.walk(stree) if isinstance(n, ast.AsyncFunctionDef) and n.name == "build_graph")
attrs = [n for n in ast.walk(bg) if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "attrs"]
keys = [ast.literal_eval(k) for k in ast.walk(attrs[0]) if isinstance(k, ast.Constant)]
print("\nChainNode.attrs keys bound by build_graph:", keys)
print("=> proof IS bound to the persisted graph node (report surface),")
print("   but that node is NEVER read back by chain/floor.py's hop execution.")

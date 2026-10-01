import json, socket, time
D="/var/lib/scanner/16e69f07-f908-482b-8fc5-492852a61a91/1f5fe7c8-5e28-45bc-8e08-a3e868bad87e"
ev=[json.loads(l) for l in open(D+"/oob_interactions.jsonl")]
ev.sort(key=lambda d: d["timestamp"])
print("=== timeline: last events ===")
for d in ev[-6:]:
    print(d["timestamp"], d["protocol"], d["remote-address"], d["full-id"].split(".")[0])
print()
print("=== source IPs seen at OOB ===")
from collections import Counter
print(Counter(d["remote-address"] for d in ev))
print()
print("=== local egress IP (what the target would see) ===")
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
try:
    s.connect(("1.1.1.1",80)); print("egress:", s.getsockname()[0])
except Exception as e: print("egress unknown:", e)
print()
print("=== curl exit 26 meaning: file/stream could not be read -> request never sent ===")
print("floor_upload_0_inject.log exit_code: 26, HTTP_STATUS:000 -> payload never delivered")
print()
print("=== why: multi-part file upload against a path WAF denies => curl aborts on first (HEAD/probe) ===")

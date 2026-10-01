import sys, json
sys.path.insert(0,'AT')
from p1_inj import send, base_fields, AT

cands = [
  "info"+AT+"infinitycapital.bh",
  '"info'+AT+'infinitycapital.bh"',
  '["info'+AT+'infinitycapital.bh"]',
  'info'+AT+"infinitycapital.bh,ceo"+AT+"infinitycapital.bh",
  '{"to":"info'+AT+'infinitycapital.bh"}',
]
for c in cands:
    f = base_fields(); f["targets"]=c
    st,body,dt = send(f)
    print(repr(c)[:70], "->", st, body[:220])

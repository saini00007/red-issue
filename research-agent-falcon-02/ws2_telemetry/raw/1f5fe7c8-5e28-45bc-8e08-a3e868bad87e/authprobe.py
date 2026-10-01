#!/usr/bin/env python3
import requests, json, sys
B="https://www.infinitycapital.bh"
s=requests.Session()
s.headers.update({"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
 "Accept":"application/json,text/html,*/*"})
paths=["/api/login","/api/auth/login","/api/authenticate","/api/auth","/api/register","/api/signup",
 "/api/users","/api/me","/api/admin","/api/token","/api/session","/api/graphql","/graphql",
 "/admin","/dashboard","/portal","/account","/wp-login.php","/_next/auth","/api/send"]
for p in paths:
    for m in ("GET","POST"):
        try:
            r=s.request(m,B+p,data=None if m=="GET" else {"email":"t@infinitycapital.bh","password":"x","username":"t"},timeout=25)
            body=r.text[:200].replace("\n"," ")
            print(f"{m} {p} -> {r.status_code} loc={r.headers.get('location','')} len={len(r.content)} setcookie={r.headers.get('set-cookie','')[:80]} :: {body[:140]}")
        except Exception as e:
            print(m,p,"ERR",e)
print("=== cookies after GET / ===")
r=s.get(B,timeout=25)
print(dict(s.cookies))

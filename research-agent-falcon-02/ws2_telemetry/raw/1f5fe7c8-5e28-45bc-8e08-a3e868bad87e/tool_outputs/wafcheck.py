import requests, re
UA={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36'}
u='https://'+'images.ctfassets.net'+'/x.jpg'
r=requests.get('https://www.infinitycapital.bh/_next/image',params={'url':u,'w':'640'},headers=UA,timeout=20)
t=r.text
print('len',len(t),'status',r.status_code)
for m in re.findall(r'<title>(.*?)</title>',t)[:2]: print('TITLE:',m)
tl=t.lower()
print('challenge:', 'challenge' in tl, 'botid:', 'botid' in tl, 'checkpoint:', 'checkpoint' in tl, 'just a moment:', 'just a moment' in tl)

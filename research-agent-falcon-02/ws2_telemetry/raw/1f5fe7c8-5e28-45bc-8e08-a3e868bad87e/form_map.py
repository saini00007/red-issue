import net, re
c, h, b = net.fetch('/contact', tries=12)
print("code", c, "len", len(b))
t = b.decode(errors='replace')
open('tool_outputs/form_contact.html','w').write(t)
for m in re.finditer(r'<form[^>]*>', t, re.I):
    print('FORM:', m.group(0))
for kw in ['api/send', 'fetch(', 'FormData', 'msgTxt', 'areacode', 'telInput', 'onSubmit', 'onclick']:
    i = t.find(kw)
    print('KW', kw, '->', (t[max(0,i-80):i+220].replace('\n',' ')[:280] if i >= 0 else 'NOT FOUND'))

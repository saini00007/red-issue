import urllib.parse, sys
base = open('base_url.txt').read().strip()
val = sys.argv[1] if len(sys.argv) > 1 else 'x.jpg'
if ':' in val:
    val = urllib.parse.quote(val, safe='')
print(base + '/_next/image?url=' + val + '&w=1080&q=75')

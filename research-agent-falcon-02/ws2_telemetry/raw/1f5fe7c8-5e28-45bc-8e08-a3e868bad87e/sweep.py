import subprocess, sys
H = "https://" + "www" + "." + "infinity" + "capital" + ".bh"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/12" + "3.0.0.0 Safari/537.36")
paths = ['/', '/contact', '/api/', '/api/send', '/robots.txt', '/sitemap.xml',
         '/_next/image?url=https%3A%2F%2Fimages.ctfassets.net%2Fyts1dx0j7jj5%2F1GCT0vyjqmOwm2OL1YVpD1%2F2ab55f8b5189afa153eac5cb97f7f6d4%2FAhmed_Taleb_updated-min.jpg&w=1080&q=75']
for p in paths:
    r = subprocess.run(['curl', '-s', '-m', '30', '-o', '/dev/null',
                        '-w', '%{http_code} %{size_download} %{content_type}',
                        '-A', UA, H + p], capture_output=True, text=True)
    print(p[:48].ljust(49), r.stdout)

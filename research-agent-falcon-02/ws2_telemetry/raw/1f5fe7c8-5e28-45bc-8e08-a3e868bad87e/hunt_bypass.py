import requests, hashlib
TARGET = "https://www.infinitycapital.bh"
def H(**extra):
    h = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari', 'Accept': '*/*'}
    h.update(extra)
    return h

cands = {
 "accept_curl": {'User-Agent': 'curl/8.4.0', 'Accept': '*/*'},
 "accept_html": {'Accept': 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.8'},
 "sec_fetch": {'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-origin', 'Sec-Fetch-Dest': 'empty'},
 "googlebot": {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)', 'Accept': '*/*'},
 "vercel_bot": {'User-Agent': 'VercelBot', 'Accept': '*/*'},
 "empty_ua": {'User-Agent': '', 'Accept': '*/*'},
 "curl_only": {'User-Agent': 'curl/8.4.0'},
 "accept_json": {'Accept': 'application/json'},
 "sec_ch_ua": {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
               'sec-ch-ua': '"Chromium";v="131", "Not_A Brand";v="24"', 'sec-ch-ua-mobile': '?0',
               'sec-ch-ua-platform': '"Windows"', 'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-origin'},
 "xfwd": {'X-Forwarded-For': '1.1.1.1'},
 "referer_self": {'Referer': TARGET + '/'},
 "xhr": {'X-Requested-With': 'XMLHttpRequest'},
 "bingbot": {'User-Agent': 'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)', 'Accept': '*/*'},
}
for name, h in cands.items():
    try:
        S = requests.Session(); S.headers.update(H(**h))
        r = S.get(TARGET + "/404?q=MARK1", timeout=15, allow_redirects=False)
        print("%-16s %s len=%7d mit=%-10s reflect=%s" % (name, r.status_code, len(r.content), r.headers.get('x-vercel-mitigated', '-'), b'MARK1' in r.content))
    except Exception as e:
        print(name, "EXC", e)

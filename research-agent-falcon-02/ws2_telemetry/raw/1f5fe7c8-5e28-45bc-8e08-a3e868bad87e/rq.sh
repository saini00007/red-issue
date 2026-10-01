#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"
H=(-sk -A "$UA"
 -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
 -H 'Accept-Language: en-US,en;q=0.9'
 -H 'sec-ch-ua: "Chromium";v="131", "Google Chrome";v="131", "Not-A.Brand";v="99"'
 -H 'sec-ch-ua-mobile: ?0' -H 'sec-ch-ua-platform: "Windows"'
 -H 'Sec-Fetch-Dest: document' -H 'Sec-Fetch-Mode: navigate' -H 'Sec-Fetch-Site: none' -H 'Sec-Fetch-User: ?1'
 -H 'Upgrade-Insecure-Requests: 1')
curl "${H[@]}" "$@"

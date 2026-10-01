#!/bin/sh
W=/var/lib/scanner/16e69f07-f908-482b-8fc5-492852a61a91/84aea81a-7e43-495c-9974-ca064ddd3552
echo "===== decisions.log ====="
cat "$W/decisions.log" 2>&1
echo "===== logs dir ====="
ls -la "$W/logs" 2>&1 | head -20
echo "===== workdir top-level mtimes ====="
ls -la --time-style=+%H:%M "$W" 2>&1 | head -60
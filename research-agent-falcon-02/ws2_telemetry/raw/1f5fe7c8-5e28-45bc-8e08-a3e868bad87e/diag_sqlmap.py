#!/usr/bin/env python3
"""Diagnose why sqlmap invocations hang: is another sqlmap holding sessions.sqlite?"""
import subprocess, os, glob, time

# 1. which sqlmap processes are alive and for how long
out = subprocess.run(['ps', '-eo', 'pid,etimes,cmd'], capture_output=True, text=True).stdout
live = [l for l in out.splitlines() if 'sqlmap' in l and 'defunct' not in l and 'grep' not in l]
print("=== live sqlmap (%d) ===" % len(live))
for l in live[:20]:
    print(l[:150])

# 2. who has the sqlite session db open
print("=== fuser on sqlmap sessions.sqlite ===")
dbs = glob.glob(os.path.expanduser('~/.local/share/sqlmap*/sessions.sqlite')) + \
      glob.glob(os.path.expanduser('~/.sqlmap*/sessions.sqlite')) + \
      glob.glob('/tmp/sqlmap*/sessions.sqlite') + \
      glob.glob(os.path.expanduser('~/.cache/sqlmap*/sessions.sqlite'))
print("dbs found:", dbs)
for d in dbs:
    try:
        subprocess.run(['fuser', '-v', d], capture_output=True, text=True, timeout=10)
    except Exception as e:
        print(e)

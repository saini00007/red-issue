#!/bin/bash
CH="$HOME/.cache/ms-playwright/chromium-1187/chrome-linux/chrome"
PROF=$(mktemp -d)
"$CH" --headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage \
  --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36" \
  --user-data-dir="$PROF" --virtual-time-budget=20000 --dump-dom "$1" 2>/dev/null

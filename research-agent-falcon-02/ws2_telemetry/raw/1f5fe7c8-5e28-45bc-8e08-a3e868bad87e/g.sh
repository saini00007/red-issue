#!/bin/bash
# usage: ./g.sh <url> [extra curl args...]
U=$(cat /work/uafile)
curl -sk -A "$U" "$@"

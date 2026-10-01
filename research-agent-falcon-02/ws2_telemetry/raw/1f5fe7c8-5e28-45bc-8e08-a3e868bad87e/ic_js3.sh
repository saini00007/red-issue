#!/bin/bash
echo "=== /api/send call context ==="
grep -o '.\{600\}"/api/send".\{1200\}' /tmp/alljs.txt | head -2

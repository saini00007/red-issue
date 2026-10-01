#!/bin/bash
echo "=== subjects / targets options from JS ==="
grep -oE 'subjects:\[.\{0,600\}' /tmp/alljs.txt | head -2
echo "=== 'targets' context ==="
grep -oE '.{200}targets:.{300}' /tmp/alljs.txt | head -3
echo "=== D6 / sanitize def ==="
grep -oE 'D6:.{0,300}' /tmp/alljs.txt | head -2

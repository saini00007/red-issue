#!/bin/sh
L=/tmp/al.$$
docker logs scanner-agent-84aea81a7e43 > $L 2>&1
echo "===== worker.started / finished timeline ====="
grep -E 'event_type=worker\.(started|finished)' $L | awk '{print $1, $2, $NF}' | head -n 70
echo
echo "===== reconcile.tick timeline ====="
grep -E 'event_type=reconcile.tick' $L | awk '{print $1, $2}'
echo
echo "===== floor.complete / sweep_failed / phase / governor ====="
grep -E 'exploit_floor\.(complete|sweep_failed)|event_type=phase\.|event_type=governor|soft_cap|engine\.level_resolved' $L | cut -c1-200
echo
echo "===== total span ====="
head -n 1 $L | cut -c1-30
tail -n 1 $L | cut -c1-30
rm -f $L
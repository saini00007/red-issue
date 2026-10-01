#!/bin/bash
run(){
  name="$1"; url="$2"
  sqlmap -u "$url" --batch --level=5 --risk=3 --dbs --threads=4 \
    --flush-session --output-dir="$PWD/sq/$name" --technique=BEUSTQ \
    > "$PWD/sq/$name.out" 2>&1
  echo "$name done rc=$?"
}

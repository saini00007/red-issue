#!/bin/sh
L=/tmp/al2.$$
docker logs scanner-agent-84aea81a7e43 2>&1 \
 | grep -E 'event_type=tool\.(started|done)' \
 | awk '{print $1" "$2, ($0 ~ /tool\.started/) ? "S" : "D"}' > $L
echo "===== first/last tool event ====="
head -n 1 $L; tail -n 1 $L
echo "===== tool events per 5-min bucket (S=started,D=done) ====="
awk '{split($1,d,"-"); split($2,t,":"); b=int((t[1]*60+t[2])/5)*5; key=substr($1,1,5)" "sprintf("%02d",b/60)":"sprintf("%02d",b%60); c[key" "$3]++} END{for(k in c) print k, c[k]}' $L | sort | head -n 60
echo "===== in-flight concurrency sampled每30s ====="
awk '{split($1,d,"-"); split($2,t,":"); s=t[1]*3600+t[2]*60+t[3]; print s, $3}' $L | sort -n > /tmp/ts.$$
awk 'BEGIN{m=0} {ev[$1]=$2; ts[NR]=$1} END{
  printf "min_s max_s\n";
  # simple event sweep
}' /tmp/ts.$$
sort -n /tmp/ts.$$ | awk '{print $1, ($2=="S")?1:-1}' | awk '
{ t[NR]=$1; d[NR]=$2 }
END{
  cur=0; area=0; prev=t[1]; peak=0;
  for(i=1;i<=NR;i++){ cur+=d[i]; if(cur>peak)peak=cur; area+=cur*(t[i]-prev); prev=t[i] }
  printf "span_s=%.0f  mean_concurrency=%.2f  peak_concurrency=%d  events=%d\n", t[NR]-t[1], area/(t[NR]-t[1]), peak, NR
}'
rm -f $L /tmp/ts.$$
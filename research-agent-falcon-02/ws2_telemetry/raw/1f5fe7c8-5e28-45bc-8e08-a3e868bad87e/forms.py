import subprocess,sys,json,os
W=os.environ['WORK_PATH']
def req(path, data=None, ctype='form', method='POST', hdrs=None):
    cmd=['bash',W+'/rq.sh','-X',method,'-w','\n%{http_code}']
    if hdrs:
        for h in hdrs: cmd+=['-H',h]
    if data is not None:
        if ctype=='form': cmd+=['-F',data]
        else: cmd+=['-H','Content-Type: '+ctype,'--data-binary',data]
    cmd.append('https://www.infinitycapital.bh'+path)
    r=subprocess.run(cmd,capture_output=True,text=True)
    return r.stdout

if __name__=='__main__':
    base='fname=Test&lname=User&areacode=973&tel=1234567&cname=QA&subject=Hello&msg=Hello%20there&check=&targets=General%20Enquiry'
    print("=== BASELINE POST /api/send ===")
    print(req('/api/send',data=base)[:800])
    print("=== GET /api/send ===")
    print(req('/api/send',method='GET')[:400])
    print("=== POST /api/ ===")
    print(req('/api/',data=base)[:400])

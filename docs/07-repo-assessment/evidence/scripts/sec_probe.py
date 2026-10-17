import os,sys,subprocess,socket,time,urllib.request,urllib.error,json,http.client,concurrent.futures as cf
ROOT=sys.argv[1]
s=socket.socket();s.bind(('127.0.0.1',0));port=s.getsockname()[1];s.close()
p=subprocess.Popen([sys.executable,'-m','app.server'],cwd=ROOT,env={**os.environ,'PORT':str(port),'HOST':'127.0.0.1'},stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
for _ in range(50):
    try: urllib.request.urlopen(f'http://127.0.0.1:{port}/health',timeout=1);break
    except Exception: time.sleep(.1)
def raw(path,headers=None,method='GET'):
    c=http.client.HTTPConnection('127.0.0.1',port,timeout=5)
    try:
        c.request(method,path,headers=headers or {});r=c.getresponse();b=r.read();return r.status,dict(r.getheaders()),b[:150]
    except Exception as e: return 'EXC',type(e).__name__,str(e)[:80]
out={}
for path in ['/api/cases/%ff','/api/cases?limit=99999999999999999999999999','/api/cases?limit=1e3','/api/cases/..%2f..%2fetc%2fpasswd','/api/partners/partner_feeds;x','//api/cases','/api/cases?limit=5&limit=7','/' + 'a'*70000]:
    st,h,b=raw(path);out[path[:60]]=(st,{k:v for k,v in h.items() if k in('Content-Type','Server','Access-Control-Allow-Origin','X-Content-Type-Options')} if isinstance(h,dict) else h,b)
t=time.time()
with cf.ThreadPoolExecutor(20) as ex: res=list(ex.map(lambda i: raw('/api/cases?limit=100')[0],range(100)))
out['100_parallel_requests_statuses']=(sorted(set(map(str,res))),round(time.time()-t,2))
p.terminate();err=p.stderr.read().decode()[-600:]
for k,v in out.items():print(k,'=>',v)
print('STDERR tail:',err)

import json,sqlite3,sys,subprocess,urllib.request,os,time,socket
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run():
    subprocess.run([sys.executable,'-m','app.workshop_check'],cwd=ROOT,check=True,stdout=subprocess.PIPE)
    with sqlite3.connect(ROOT/'data'/'legacy.sqlite3') as c:
        assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        assert not c.execute('PRAGMA foreign_key_check').fetchall()
    sock=socket.socket();sock.bind(('127.0.0.1',0));port=sock.getsockname()[1];sock.close()
    env={**os.environ,'PORT':str(port),'HOST':'127.0.0.1'}
    proc=subprocess.Popen([sys.executable,'-m','app.server'],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    try:
        for _ in range(50):
            try:
                with urllib.request.urlopen(f'http://127.0.0.1:{port}/health',timeout=1) as r: assert json.loads(r.read())['status']=='ok'
                break
            except Exception:time.sleep(.1)
        else:raise RuntimeError('API did not become healthy')
        with urllib.request.urlopen(f'http://127.0.0.1:{port}/api/metrics',timeout=3) as r:assert json.loads(r.read())['total_cases']>0
        return {'api':'pass','database':'pass'}
    finally:
        proc.terminate()
        try:proc.wait(timeout=3)
        except subprocess.TimeoutExpired:proc.kill()
if __name__=='__main__':print(json.dumps(run()))

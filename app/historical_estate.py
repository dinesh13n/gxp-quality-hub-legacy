"""Versioned file-drop bridge. Deliberately old-fashioned batch integration; no AI dependency."""
import argparse,csv,datetime,hashlib,json,os,random,sqlite3
from pathlib import Path
from .store import connect
ROOT=Path(__file__).resolve().parents[1]
def import_csv(file_path):
    path=Path(file_path); imported=0; skipped=0
    with connect() as c:
        c.execute('CREATE TABLE IF NOT EXISTS vendor_file_imports(id TEXT PRIMARY KEY, source_file TEXT, received_at TEXT, count INTEGER, state TEXT)')
        c.execute('CREATE TABLE IF NOT EXISTS vendor_file_rows(import_id TEXT, line_no INTEGER, tenant TEXT, external_id TEXT, message_kind TEXT, amount_text TEXT, received_ts TEXT, payload TEXT, PRIMARY KEY(import_id,line_no))')
        digest=hashlib.sha256(path.read_bytes()).hexdigest()[:24]
        exists=c.execute('SELECT 1 FROM vendor_file_imports WHERE id=?',(digest,)).fetchone()
        if exists:return {'status':'already_imported','import_id':digest,'rows':0}
        with path.open(encoding='utf-8-sig',newline='') as f:
            for n,r in enumerate(csv.DictReader(f),start=1):
                # Legacy file-drop retains raw representation instead of validating currency or tenant.
                c.execute('INSERT INTO vendor_file_rows VALUES (?,?,?,?,?,?,?,?)',(digest,n,r.get('tenant',''),r.get('external_id',''),r.get('kind',''),r.get('amount',''),r.get('recorded_at',''),json.dumps(r,ensure_ascii=False)))
                imported+=1
        c.execute('INSERT INTO vendor_file_imports VALUES (?,?,?,?,?)',(digest,path.name,datetime.datetime.now(datetime.timezone.utc).isoformat(),imported,'ACCEPTED'))
    return {'status':'accepted','import_id':digest,'rows':imported}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('path');args=parser.parse_args();print(json.dumps(import_csv(args.path)))
if __name__=='__main__':main()

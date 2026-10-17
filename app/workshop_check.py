"""Offline runnable self-check. No data mutation beyond schema initialization."""
import json,sqlite3,sys
from .store import connect,setup
from .partner_feeds import init,PROFILE
def main():
 init()
 needed=['cases','events','source_messages','partner_feeds','reference_versions','policy_exceptions','upstream_outages','batch_runs']
 with connect() as db:
  tables={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
  counts={t:db.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t in needed if t in tables}
  fk=db.execute('PRAGMA foreign_key_check').fetchall()
  integrity=db.execute('PRAGMA integrity_check').fetchone()[0]
 out={'profile':PROFILE['context'],'counts':counts,'foreign_key_errors':len(fk),'integrity':integrity,'ok':all(t in tables and counts.get(t,0)>0 for t in needed) and not fk and integrity=='ok'}
 print(json.dumps(out));return 0 if out['ok'] else 1
if __name__=='__main__':sys.exit(main())

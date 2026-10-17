"""Offline participant-machine readiness and baseline check."""
import os,sys,unittest,json,sqlite3,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
issues=[]
for filename in ['data/legacy.sqlite3','data/enterprise_legacy.sqlite3']:
 p=root/filename
 if not p.exists():issues.append('missing '+filename);continue
 with sqlite3.connect(p) as con:
  if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok':issues.append('corrupt '+filename)
  if con.execute('PRAGMA foreign_key_check').fetchall():issues.append('invalid FK '+filename)
print(json.dumps({'python':sys.version.split()[0],'offline_ready':not issues,'problems':issues}))
raise SystemExit(bool(issues))

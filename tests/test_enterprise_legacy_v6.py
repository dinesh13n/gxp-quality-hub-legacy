import unittest, tempfile, sqlite3, json
from pathlib import Path
from app.enterprise_legacy import generate
from legacy_batch.shift_reconciliation import run
class EnterpriseLegacyTests(unittest.TestCase):
 def test_reproducible_entities_and_foreign_keys(self):
  with tempfile.TemporaryDirectory() as d:
   db=Path(d)/'domain.sqlite3';a=generate(rows=120,seed=42,db=db)
   self.assertEqual(a['integrity'],'ok');self.assertEqual(a['fk_violations'],0)
   self.assertEqual(a['entities']['operational_objects'],120)
   self.assertEqual(a['entities']['evidence_events'],120)
   s=run(80,db=db)
   self.assertEqual(s['processed'],80)
   self.assertEqual(sum(s['by_tenant'].values()),80)
 def test_repeat_seed_same_first_row(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'repeat.sqlite3';generate(120,42,p)
   with sqlite3.connect(p) as c: first=c.execute('SELECT value FROM operational_objects ORDER BY object_id LIMIT 1').fetchone()[0]
   generate(120,42,p)
   with sqlite3.connect(p) as c: second=c.execute('SELECT value FROM operational_objects ORDER BY object_id LIMIT 1').fetchone()[0]
   self.assertEqual(first,second)
if __name__=='__main__':unittest.main()

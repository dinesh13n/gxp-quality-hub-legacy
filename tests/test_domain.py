import os,tempfile,unittest
from pathlib import Path
class DomainTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();os.environ['LEGACY_DB']=str(Path(self.tmp.name)/'test.sqlite3')
  from app.generate import generate
  generate(180,4100,True)
 def tearDown(self):
  os.environ.pop('LEGACY_DB',None);self.tmp.cleanup()
 def test_relationships(self):
  from app.store import connect
  with connect() as c:
   self.assertEqual(c.execute('select count(*) from materials').fetchone()[0],30)
   self.assertEqual(c.execute('select count(*) from batch_records').fetchone()[0],180)
   self.assertEqual(c.execute('pragma foreign_key_check').fetchall(),[])

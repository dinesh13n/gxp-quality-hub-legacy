import unittest
from app.store import connect,setup
from app.enterprise_data import TABLES
class EnterpriseDataTests(unittest.TestCase):
 def test_domain_tables_populated(self):
  setup()
  with connect() as c:
   for table,_ in TABLES:
    self.assertGreater(c.execute('SELECT COUNT(*) FROM '+table).fetchone()[0],0,table)
 def test_foreign_keys(self):
  with connect() as c:
   self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(),[])

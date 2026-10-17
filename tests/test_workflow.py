import os,tempfile,unittest
from pathlib import Path
class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); os.environ['LEGACY_DB']=str(Path(self.tmp.name)/'test.sqlite3')
        from app.generate import generate
        generate(125,4100,True)
    def tearDown(self):
        os.environ.pop('LEGACY_DB',None); self.tmp.cleanup()
    def test_fixture_and_counts(self):
        from app.store import connect
        with connect() as c:
            self.assertEqual(c.execute('SELECT COUNT(*) FROM cases').fetchone()[0],125)
            self.assertEqual(c.execute('SELECT COUNT(*) FROM events').fetchone()[0]>=125,True)
    def test_baseline(self):
        from app.baseline import baseline
        b=baseline();self.assertEqual(b['records'],125);self.assertGreater(b['hours_per_case'],0)
    def test_priority(self):
        from app.legacy_logic import priority
        self.assertEqual(priority('CLOSED','LOW',99999),'archive')
        self.assertEqual(priority('OPEN','CRITICAL',1),'urgent')
    def test_feed_parser(self):
        from app.integration import consume_source_messages
        self.assertIsInstance(consume_source_messages(3),list)
if __name__=='__main__':unittest.main()

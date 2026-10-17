import unittest,tempfile,csv,sqlite3,json
from pathlib import Path
from app.historical_fixture import generate
class HistoricalFixtureTests(unittest.TestCase):
    def test_seeded_and_relational(self):
        with tempfile.TemporaryDirectory() as folder:
            m=generate('tiny',7421,folder)
            self.assertEqual(m['transaction_rows'],2400)
            self.assertEqual(m['event_rows'],9500)
            path=Path(folder)
            with (path/'partner_export.csv').open(encoding='utf-8') as f:self.assertEqual(sum(1 for _ in csv.reader(f)),2401)
            with sqlite3.connect(path/'reference.sqlite3') as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM master_data').fetchone()[0],480)
            with sqlite3.connect(path/'finance.sqlite3') as c:self.assertGreater(c.execute('SELECT COUNT(*) FROM ledger').fetchone()[0],0)
            self.assertEqual(len(list((path/'documents').glob('*.json'))),360)

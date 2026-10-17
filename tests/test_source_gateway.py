import json,unittest,os,tempfile,sqlite3
from pathlib import Path
from app import gateway_bridge,operational_report
CFG=json.loads((Path(__file__).resolve().parents[1]/'integration'/'source-gateway.json').read_text())
class TestGatewayAndDomain(unittest.TestCase):
    def test_relations(self):
        report=operational_report.run()
        self.assertGreater(report['parent_records'],0)
        self.assertGreater(report['detail_records'],0)
        self.assertGreaterEqual(report['parents_with_detail'],1)
    def test_idempotent_ingestion(self):
        from app.store import connect
        with connect() as c: key=c.execute('SELECT '+CFG['parent_key']+' FROM '+CFG['parent_table']+' LIMIT 1').fetchone()[0]
        e={'message_id':'CHECK-'+CFG['event_kind'],'business_key':key,'system':CFG['sources'][0],'event_type':CFG['event_types'][0],'occurred_at':'2025-01-01T00:00:00Z'}
        one=gateway_bridge.apply([e]);two=gateway_bridge.apply([e]);self.assertIn(one['accepted'],(0,1));self.assertEqual(two['duplicates'],1)
    def test_invalid_rejected(self):
        self.assertEqual(gateway_bridge.apply([{'message_id':'bad'}])['invalid'],1)
if __name__=='__main__':unittest.main()

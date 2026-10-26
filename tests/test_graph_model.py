import os,sqlite3,tempfile,unittest
from pathlib import Path
from graph import model
ROOT=Path(__file__).resolve().parents[1]
class GraphModelTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  # app.store fixes DB at first import; patch it so generate(reset=True) can never touch data/legacy.sqlite3
  import app.store as store
  from app.generate import generate
  cls.tmp=tempfile.TemporaryDirectory();cls.db=str(Path(cls.tmp.name)/'test.sqlite3')
  cls._old=store.DB;store.DB=Path(cls.db)
  assert Path(store.DB).parent==Path(cls.tmp.name)
  try:generate(180,4100,True)
  finally:store.DB=cls._old
 @classmethod
 def tearDownClass(cls):
  cls.tmp.cleanup()
 def assertNoDangling(self,g):
  for (t,sl,dl),items in g.edges.items():
   for s,d,_ in items:
    self.assertIn(s,g.nodes[sl],t);self.assertIn(d,g.nodes[dl],t)
 def test_quality_graph_matches_source(self):
  g=model.build(self.db)
  c=sqlite3.connect(self.db);n=lambda t:c.execute('select count(*) from '+t).fetchone()[0]
  nodes,edges=g.counts()
  self.assertEqual(nodes['Case'],n('cases'));self.assertEqual(nodes['Batch'],n('batch_records'))
  self.assertEqual(nodes['CAPA'],n('capa_actions'));self.assertEqual(nodes['Site'],6)
  self.assertEqual(edges['HAS_EVENT:Case->CaseEvent'],n('events'));self.assertEqual(edges['HAS_DEVIATION:Batch->Deviation'],n('deviations'))
  c.close();self.assertNoDangling(g)
 def test_source_untouched_and_no_free_text(self):
  before=Path(self.db).read_bytes();g=model.build(self.db)
  self.assertEqual(Path(self.db).read_bytes(),before)
  self.assertTrue(all('note' not in p and 'payload' not in p for v in g.nodes.values() for p in v.values()))
 def test_enterprise_graph(self):
  ent=ROOT/'data'/'enterprise_legacy.sqlite3'
  if not ent.exists():self.skipTest('enterprise archive not present')
  g=model.build(self.db,str(ent));nodes,edges=g.counts()
  self.assertEqual(edges['RELATES_TO:OperationalObject->OperationalObject'],4166)
  self.assertNoDangling(g)
 def test_exports_consistent(self):
  import json,xml.dom.minidom
  from graph import export
  out=str(Path(self.tmp.name)/'kg');export.main(['--legacy-db',self.db,'--no-enterprise','--out',out])
  d=json.load(open(Path(out)/'knowledge-graph.json',encoding='utf-8'));keys={n['key'] for n in d['nodes']}
  self.assertTrue(all(e['source'] in keys and e['target'] in keys for e in d['links']))
  x=xml.dom.minidom.parse(str(Path(out)/'knowledge-graph.graphml'))
  self.assertEqual(len(x.getElementsByTagName('node')),len(d['nodes']));self.assertEqual(len(x.getElementsByTagName('edge')),len(d['links']))
  self.assertIn('vis-network@9.1.9',(Path(out)/'knowledge-graph.html').read_text(encoding='utf-8'))
if __name__=='__main__':unittest.main()

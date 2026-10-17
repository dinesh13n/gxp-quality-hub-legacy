import unittest, tempfile, os
from pathlib import Path
from unittest.mock import patch
class TestPartnerFeeds(unittest.TestCase):
 def test_contract(self):
  from app.partner_feeds import PROFILE
  self.assertGreaterEqual(len(PROFILE['policies']),4)
  self.assertGreaterEqual(len(PROFILE['part']),4)
 def test_required_tables(self):
  from app.partner_feeds import init
  from app.store import connect
  init()
  with connect() as db:
   for name in ['partner_feeds','reference_versions','policy_exceptions','upstream_outages','batch_runs']:
    self.assertIsNotNone(db.execute('SELECT name FROM sqlite_master WHERE name=?',(name,)).fetchone())

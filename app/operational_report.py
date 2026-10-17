"""Domain-dependent current-state operational correlation report."""
import json, argparse
from .store import connect,setup
from pathlib import Path
CFG=json.loads((Path(__file__).resolve().parents[1]/'integration'/'source-gateway.json').read_text())
def run():
    setup()
    with connect() as c:
        n=c.execute('SELECT COUNT(*) FROM '+CFG['parent_table']).fetchone()[0]
        detail=c.execute('SELECT COUNT(*) FROM '+CFG['child_table']).fetchone()[0]
        joined=c.execute('SELECT COUNT(DISTINCT p.'+CFG['parent_key']+') FROM '+CFG['parent_table']+' p LEFT JOIN '+CFG['child_table']+' d ON p.'+CFG['parent_key']+'=d.'+CFG['child_key']+' WHERE d.'+CFG['child_key']+' IS NOT NULL').fetchone()[0]
        try: inbox=c.execute('SELECT COUNT(*) FROM gateway_inbox').fetchone()[0]
        except Exception: inbox=0
    return {'domain':CFG['domain'],'parent_records':n,'detail_records':detail,'parents_with_detail':joined,'parents_without_detail':n-joined,'ingested_source_messages':inbox}
if __name__=='__main__':print(json.dumps(run(),indent=2))

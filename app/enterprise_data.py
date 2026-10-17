import datetime, json, random
from .store import connect
TABLES = [('deviations', 'deviation_id TEXT PRIMARY KEY, batch_id TEXT NOT NULL REFERENCES batch_records(batch_id), opened_at TEXT NOT NULL, classification TEXT NOT NULL, root_cause TEXT, status TEXT NOT NULL'), ('lab_results', 'result_id TEXT PRIMARY KEY, batch_id TEXT NOT NULL REFERENCES batch_records(batch_id), analyte TEXT NOT NULL, result_value REAL, unit TEXT NOT NULL, test_status TEXT NOT NULL, measured_at TEXT NOT NULL'), ('capa_actions', 'capa_id TEXT PRIMARY KEY, deviation_id TEXT NOT NULL REFERENCES deviations(deviation_id), action_owner TEXT NOT NULL, due_at TEXT NOT NULL, state TEXT NOT NULL'), ('sop_versions', 'sop_id TEXT NOT NULL, version TEXT NOT NULL, effective_at TEXT NOT NULL, retired_at TEXT, PRIMARY KEY(sop_id,version)')]
DOMAIN = 'Pharma'
PHRASES = ['OOS investigation pending signature from QA', 'draft procedure superseded after sampling', 'batch genealogy discrepancy between LIMS and MES']

def expand(seed=4100):
    rng = random.Random(seed + 77019)
    with connect() as c:
        for name,ddl in TABLES:
            c.execute('CREATE TABLE IF NOT EXISTS '+name+'('+ddl+')')
        for name,_ in reversed(TABLES):
            c.execute('DELETE FROM '+name)
        parents = [x[0] for x in c.execute('SELECT material_id FROM materials')]
        n=len(parents)
        if not n: raise RuntimeError('Domain data missing: generate base data first')
        date0=datetime.datetime(2023,1,1,tzinfo=datetime.timezone.utc)
        def ts(i):return (date0+datetime.timedelta(hours=i*7)).isoformat()
        batches=[x[0] for x in c.execute('SELECT batch_id FROM batch_records ORDER BY batch_id')]
        for i,b in enumerate(batches):
            c.execute('INSERT INTO lab_results VALUES (?,?,?,?,?,?,?)',(f'LAB{i:08d}',b,rng.choice(['assay','impurity','water']),round(rng.gauss(99,3.8),3) if rng.random()>.02 else None,rng.choice(['percent','pct']),rng.choice(['VALID','OOS','PENDING','INVALID']),ts(i)))
            if i%3==0:
                dev=f'DEV{i:08d}'
                c.execute('INSERT INTO deviations VALUES (?,?,?,?,?,?)',(dev,b,ts(i),rng.choice(['MINOR','MAJOR','CRITICAL']),rng.choice(PHRASES) if i%2 else None,rng.choice(['OPEN','INVESTIGATION','CLOSED'])))
                if i%2==0:c.execute('INSERT INTO capa_actions VALUES (?,?,?,?,?)',(f'CAPA{i:08d}',dev,rng.choice(['QA','QC','Manufacturing']),ts(i+100),rng.choice(['OPEN','OVERDUE','VERIFIED'])))
        for i in range(45):c.execute('INSERT INTO sop_versions VALUES (?,?,?,?)',(f'SOP-{i//3:03d}',f'v{i%3+1}',ts(i),ts(i+200) if i%3!=2 else None))
        return {t:c.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t,_ in TABLES}

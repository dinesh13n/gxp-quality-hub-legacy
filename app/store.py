import sqlite3, os
from contextlib import contextmanager
from pathlib import Path
DB = Path(os.environ.get('LEGACY_DB', str(Path(__file__).resolve().parents[1] / 'data' / 'legacy.sqlite3')))
@contextmanager
def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    conn.execute('PRAGMA busy_timeout=15000')
    try:
        with conn:
            yield conn
    finally:
        conn.close()
def setup():
    with connect() as c:
        c.executescript('CREATE TABLE IF NOT EXISTS cases(id TEXT PRIMARY KEY, account_id TEXT NOT NULL, segment TEXT NOT NULL, site TEXT NOT NULL, region TEXT NOT NULL, created_at TEXT NOT NULL, status TEXT NOT NULL, severity TEXT NOT NULL, amount REAL NOT NULL, note TEXT NOT NULL, version INTEGER NOT NULL DEFAULT 1);\nCREATE TABLE IF NOT EXISTS events(id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(id), recorded_at TEXT NOT NULL, event_type TEXT NOT NULL, payload TEXT NOT NULL);\nCREATE TABLE IF NOT EXISTS source_messages(id TEXT PRIMARY KEY, source TEXT NOT NULL, received_at TEXT NOT NULL, body TEXT NOT NULL);\nCREATE TABLE IF NOT EXISTS operating_costs(period TEXT PRIMARY KEY, labor_hours REAL NOT NULL, total_cases INTEGER NOT NULL, infrastructure_usd REAL NOT NULL);\nCREATE INDEX IF NOT EXISTS idx_cases_status ON cases(status);\nCREATE INDEX IF NOT EXISTS idx_events_case ON events(case_id);')

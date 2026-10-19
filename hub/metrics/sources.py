"""Amount sources for month-end totals (BEH-MET-05/06, AC-MET-09/11/12; INC-07).

`CasesAmountSource` reads the legacy `cases` table (through the hash-gated read-only snapshot handle, never the working-tree data/) with ONE
query on ONE table - no join to `events`, which is what fanned out the legacy report to 742,956.61 (BB-08). `RowsSource` wraps rows of text
amounts (vendor rows, feed quantities). `parse_amount` is strict: blank and unparsable values are error codes, never skipped or zero.
"""
from hub.core.errors import HubError
from hub.policy.inputs import to_decimal

CASES_SQL = "SELECT id, amount, created_at FROM cases ORDER BY id"
ALLOWED = ("cases.amount", "vendor_rows.amount_text", "feed.quantity")


class CasesAmountSource(object):
    name = "cases.amount"

    def __init__(self, db):
        self.db = db  # anything with .execute(sql, params) (ReadOnlyLegacy handle, sqlite3 connection)

    def read(self):
        return [(r[0], r[1], r[2]) for r in list(self.db.execute(CASES_SQL))]

    def plan(self):
        return [str(r[-1]) for r in list(self.db.execute("EXPLAIN QUERY PLAN " + CASES_SQL))]


class RowsSource(object):
    def __init__(self, name, rows):
        self.name, self._rows = name, list(rows)

    def read(self):
        return [(r[0], r[1], r[2] if len(r) > 2 else None) for r in self._rows]


def parse_amount(raw):
    """(Decimal, None) or (None, code): BLANK_AMOUNT | UNPARSABLE_AMOUNT. Floats go through repr (50000.01 is the decimal 50000.01)."""
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return None, "BLANK_AMOUNT"
    try:
        return to_decimal(raw, "amount"), None
    except HubError:
        return None, "UNPARSABLE_AMOUNT"


def case_sites(db):
    """{case_id: site} from the legacy cases table (one query, one table)."""
    return dict((r[0], r[1]) for r in list(db.execute("SELECT id, site FROM cases ORDER BY id")))

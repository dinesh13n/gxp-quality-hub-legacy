"""Runtime self-check (BEH-CO-09, AC-CO-14, OD-S12-12 default accepted under OD-12/OD-14).

Floor "3.10" (default): Python >= 3.10 and SQLite >= 3.37 (dev device: 3.10.12 / 3.37.2).
Floor "3.12": ADR-018 (PROPOSED) target; selectable for the class-B test of OD-S12-12 only.
FTS5 availability is reported, not required (R2 search, OD-S12-14). Keep this module free of 3.10-only syntax.
"""
import sqlite3
import sys

from hub.core.errors import ConfigInvalid, RuntimeUnsupported

FLOORS = {
    "3.10": {"python": (3, 10), "sqlite": (3, 37, 0), "source": "OD-S12-12 default (OD-14)"},
    "3.12": {"python": (3, 12), "sqlite": (3, 37, 0), "source": "ADR-018 PROPOSED target (not adopted)"},
}
DEFAULT_FLOOR = "3.10"


def parse_version(text):
    parts = [int(p) for p in str(text).strip().split(".")[:3]]
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)


def fts5_available():
    con = sqlite3.connect(":memory:")
    try:
        con.execute("CREATE VIRTUAL TABLE t USING fts5(x)")
        return True
    except sqlite3.OperationalError:
        return False
    finally:
        con.close()


def check(python_version=None, sqlite_version=None, floor=DEFAULT_FLOOR):
    """Return the version report, or raise E-CO-RUNTIME-UNSUPPORTED below the floor."""
    if floor not in FLOORS:
        raise ConfigInvalid({"runtime.floor": floor, "allowed": sorted(FLOORS)})
    py = parse_version(python_version) if python_version else tuple(sys.version_info[:3])
    sq = parse_version(sqlite_version or sqlite3.sqlite_version)
    f = FLOORS[floor]
    report = {
        "python": "%d.%d.%d" % py,
        "sqlite": "%d.%d.%d" % sq,
        "fts5": fts5_available(),
        "floor": floor,
        "floor_python": "%d.%d" % f["python"],
        "floor_sqlite": "%d.%d.%d" % f["sqlite"],
        "floor_source": f["source"],
    }
    if py[:2] < f["python"] or sq < f["sqlite"]:
        raise RuntimeUnsupported(report)
    return report

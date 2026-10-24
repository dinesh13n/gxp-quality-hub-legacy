"""Gate G6 (AC-SEC-18, BEH-SEC-07, BEH-SEC-11, PNFR-08/10): secret scan + deletion-path grep.

secret_scan(paths)   regex scan of text files for credential material (private-key blocks, cloud/API token
                     shapes, literal credential assignments). Heuristic; the full scanner choice is Stage 24.
deletion_grep(paths) finds SQL deletes against retained tables in PRODUCT code (hub/ *.py, *.sql). Tests are
                     out of scope: they attempt deletes on purpose to prove the triggers reject them.
retention_triggers(con) every retained table present in the store has a BEFORE DELETE trigger that aborts.
Patterns are assembled from fragments so this file does not match itself.
"""
import os
import re

from hub.security import tables

_BEGIN = "-----" + "BEGIN"
SECRET_PATTERNS = (
    ("private_key_block", re.compile(_BEGIN + r" (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----")),
    ("aws_access_key_id", re.compile(r"\b" + "AK" + r"IA[0-9A-Z]{16}\b")),
    ("github_token", re.compile(r"\b" + "gh" + r"[pousr]_[A-Za-z0-9]{36,}\b")),
    ("slack_token", re.compile(r"\b" + "xo" + r"x[abprs]-[A-Za-z0-9-]{10,}")),
    ("llm_api_key", re.compile(r"\b" + "s" + r"k-(?:ant-|proj-)?[A-Za-z0-9_-]{20,}")),
    ("credential_assignment", re.compile(
        r"(?i)\b(?:pass" + r"word|passwd|pwd|secret|api_?key|access_?token|auth_?token)\b\s*[:=]\s*[\"'][^\"'\s]{6,}[\"']")),
)
# Stage 24 (DW-19, RF-02): the register of table dispositions is hub/security/tables.py; every table with an aborting BEFORE DELETE trigger is listed
# there (39 tables; the Stage 15 list of 18 is a subset), and tests/hub/test_tst_hub_stg24_tables.py proves it equals the live store.
RETAINED_TABLES = tables.RETAINED_TABLES
_DELETE = re.compile(r"(?i)\b" + "DEL" + r"ETE\s+FROM\s+[\"`\[]?([A-Za-z_][A-Za-z0-9_]*)")
_DROP = re.compile(r"(?i)\b" + "DR" + r"OP\s+TABLE\s+(?:IF\s+EXISTS\s+)?[\"`\[]?([A-Za-z_][A-Za-z0-9_]*)")
TEXT_EXT = (".py", ".sql", ".json", ".md", ".txt", ".toml", ".yaml", ".yml", ".cfg", ".ini", ".sh", ".env")
SKIP_DIRS = {".git", "__pycache__", "data", "node_modules"}


def _files(paths, exts):
    for p in paths:
        if os.path.isfile(p):
            yield p
            continue
        for d, dirs, fns in os.walk(p):
            dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
            for fn in sorted(fns):
                if fn.endswith(exts) or fn.startswith(".env"):
                    yield os.path.join(d, fn)


def secret_scan(paths):
    findings = []
    for f in _files(paths, TEXT_EXT):
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                for n, line in enumerate(fh, 1):
                    for kind, rx in SECRET_PATTERNS:
                        if rx.search(line):
                            findings.append({"path": f, "line": n, "kind": kind})  # never echo the match
        except OSError as e:
            findings.append({"path": f, "line": 0, "kind": "unreadable", "detail": str(e)[:100]})
    return findings


def deletion_grep(paths):
    findings = []
    for f in _files(paths, (".py", ".sql")):
        with open(f, encoding="utf-8", errors="replace") as fh:
            for n, line in enumerate(fh, 1):
                for kind, rx in (("delete", _DELETE), ("drop_table", _DROP)):
                    for m in rx.finditer(line):
                        if m.group(1).lower() in RETAINED_TABLES:
                            findings.append({"path": f, "line": n, "kind": kind, "table": m.group(1)})
    return findings


def retention_triggers(con):
    """Return retained tables present in the store that lack an aborting BEFORE DELETE trigger."""
    tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    missing = []
    for t in RETAINED_TABLES:
        if t not in tables:
            continue
        sqls = [r[0] or "" for r in con.execute("SELECT sql FROM sqlite_master WHERE type = 'trigger' AND tbl_name = ?", (t,))]
        if not any(re.search(r"(?is)BEFORE\s+DELETE\s+ON\s+%s\b.*RAISE\s*\(\s*ABORT" % t, s) for s in sqls):
            missing.append(t)
    return missing


def run(package_root, con=None):
    hub_dir = os.path.join(package_root, "hub")
    targets = [hub_dir, os.path.join(package_root, "tests", "hub")]
    report = {"secret_findings": secret_scan([t for t in targets if os.path.exists(t)]),
              "deletion_findings": deletion_grep([hub_dir]),
              "scanned": ["hub", "tests/hub"], "deletion_scope": ["hub"]}
    if con is not None:
        report["tables_without_delete_trigger"] = retention_triggers(con)
    report["clean"] = not (report["secret_findings"] or report["deletion_findings"] or
                           report.get("tables_without_delete_trigger"))
    return report

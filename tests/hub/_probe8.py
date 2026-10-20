"""Subprocess probe for TST-NFR-17: build the web app on an existing INC-08 store and print the sha256 of the status + body of a fixed list of GET
requests. Run with different PYTHONHASHSEED / TZ / LC_ALL; the digest must not change. Usage: _probe8.py CONFIG_PATH DATA_DIR CLOCK_START TOKENS_JSON."""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))

from hub import config  # noqa: E402
from hub.security.canonical import FixedClock  # noqa: E402
from hub.web.app import Request, WebApp  # noqa: E402

CALLS = (("/api/v2/queues/exceptions", "rev"), ("/api/v2/cases/C90000001/state", "rev"), ("/api/v2/cases/C90000001/events", "rev"),
         ("/api/v2/cases/C90000001/evidence-pack", "holder-1"), ("/api/v2/cases/C90000001/rule-trace", "rev"),
         ("/api/v2/cases/C00000001/clocks", "rev"), ("/api/v2/metrics/time-to-close", "ql"),
         ("/api/v2/metrics/backlog?definition_tag=D-OPS&as_of=2030-01-01", "ql"), ("/api/v2/policies", "ql"), ("/api/v2/rulesets", "ql"),
         ("/api/v2/gate/status", "rev"), ("/api/v2/search", "rev"), ("/api/v2/nothing", "rev"))


def main(cfg_path, data_dir, clock_start, tokens_json):
    cfg = config.load(cfg_path)
    app = WebApp(data_dir, cfg, FixedClock(start=clock_start))
    tokens = json.load(open(tokens_json))
    out = {}
    for path, who in CALLS:
        p, _, q = path.partition("?")
        query = dict(x.split("=", 1) for x in q.split("&")) if q else {}
        r = app.handle(Request("GET", p, query, {"Authorization": "Bearer " + tokens[who], "X-Correlation-Id": "probe-8-fixed-correlation"}))
        out[path] = "%d %s %s" % (r.status, hashlib.sha256(r.body).hexdigest(), r.body[:160].decode("ascii", "replace").replace("\n", " "))
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main(*sys.argv[1:5])

"""Stage 23 DW-13 / DW-16: derive the Stage 12 v0.2 JSON schemas (docs/23-human-control/stage12-v0.2/schemas/) from the frozen v0.1 files
(docs/12-specs/contracts/schemas/) plus the ADDITIVE changes below, and write schema-addendum-changes.json. The v0.1 files are never edited (HAR-13).
Run from the repository root:  python3 -B docs/23-human-control/evidence/s23_make_v02_schemas.py
Rules: no new `required` entry in any schema except hub-config (a rewrite, see CHANGES), no property removed, no existing property definition narrowed.
Synthetic, unvalidated.
"""
import copy
import glob
import json
import os

REPO = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
SRC = os.path.join(REPO, "docs", "12-specs", "contracts", "schemas")
DST = os.path.join(REPO, "docs", "23-human-control", "stage12-v0.2", "schemas")
TS = {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\\.[0-9]+)?(Z|\\+00:00)$"}
STR_OR_NULL = {"type": ["string", "null"]}


def obj(props, required=None, extra=False):
    d = {"type": "object", "additionalProperties": extra, "properties": props}
    if required:
        d["required"] = required
    return d


def pos_int(minimum=1, maximum=None):
    d = {"type": "integer", "minimum": minimum}
    if maximum is not None:
        d["maximum"] = maximum
    return d


HUB_CONFIG_PROPS = {
    "data_origin": {"enum": ["synthetic", "production"], "description": "the hub accepts only 'synthetic' until HAR-15 (hub.config.validate)"},
    "hub": obj({"kill": {"type": "boolean"}}, ["kill"]),
    "runtime": obj({"floor": {"enum": ["3.10", "3.12"]}}, ["floor"]),
    "capability_authority": {"type": "object", "description": "capability -> shadow | authoritative; authoritative needs approval_refs['capability_authority.<cap>'] (DW-17, FF-2 rule 3)",
                             "additionalProperties": {"enum": ["shadow", "authoritative"]}},
    "approval_refs": {"type": "object", "description": "flag path -> reference to the recorded human approval (DW-17); the hub cannot verify the reference",
                      "additionalProperties": {"type": "string", "minLength": 1, "maxLength": 200}},
    "zone_h": obj({"holders": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": True, "description": "ships empty (FR-GATE-04)"},
                   "reauth_window_seconds": pos_int(1, 3600)}, ["holders", "reauth_window_seconds"]),
    "network": obj({"bind": {"type": "string"}, "exposure_approved": {"type": "boolean"}, "exposure_approval_ref": STR_OR_NULL,
                    "tls": obj({"cert_file": STR_OR_NULL, "key_file": STR_OR_NULL})}, ["bind", "exposure_approved", "exposure_approval_ref", "tls"]),
    "audit": obj({"anchor_path": STR_OR_NULL, "anchor_every": pos_int()}, ["anchor_path", "anchor_every"]),
    "auth": obj({"pbkdf2_iterations": pos_int(600000), "password_min_length": pos_int(12, 1024), "lockout_threshold": pos_int(),
                 "lockout_window_seconds": pos_int(), "lockout_duration_seconds": pos_int(), "session_idle_seconds": pos_int(),
                 "session_absolute_seconds": pos_int()}),
    "disposition": obj({"mode": {"enum": ["none", "event", "external_ref"]}, "values": {"type": "array", "items": {"type": "string"}}}, ["mode", "values"]),
    "closure": obj({"unconfigured_behaviour": {"enum": ["treat_label_CLOSED_as_closing", "none"]}}, ["unconfigured_behaviour"]),
    "workflow": obj({"transition_table": {"enum": ["structural", "strict"]}, "transitions": {"type": "object"}}, ["transition_table", "transitions"]),
    "facts": obj({"derivation": {"enum": ["human_only"]}}, ["derivation"]),
    "case_creation": obj({"enabled": {"type": "boolean"}}, ["enabled"]),
    "schedule": obj({"enabled": {"type": "boolean"}, "expected": {"type": "array", "items": obj({"job": {"type": "string"}, "at": {"type": "string", "pattern": "^[0-9]{2}:[0-9]{2}$"}}, ["job", "at"])},
                     "grace_minutes": pos_int()}, ["enabled"]),
    "runs": obj({"batch_size": {"type": ["integer", "null"], "minimum": 1}, "heartbeat_stale_seconds": pos_int()}),
    "site": obj({"timezone": {"type": "string"}}),
    "search": obj({"enabled": {"type": "boolean"}, "fts": {"enum": ["auto", "off"]}, "max_doc_chars": pos_int(100), "require_c3_reason": {"type": "boolean"}}),
    "templates": obj({"enabled": {"type": "boolean"}}, ["enabled"]),
    "gateway": obj({"retries": pos_int(0)}),
    "contract_bindings": None,  # kept from v0.1 unchanged (not read by the hub: bindings are policy events, DEV-55)
}

CHANGES = [
    {"schema": "intake-outcome", "ic": "IC-7", "kind": "add optional properties", "detail": "contract_missing (array of strings), conflicts_with (string|null), reason_detail (object)",
     "evidence": "M004 addendum columns; Stage 16 DC-02: 10,983 of 10,983 shipped-data outcomes failed v0.1 only on these three fields; Stage 23 DW-16 scenario 21 of 21"},
    {"schema": "metric-value", "ic": "IC-7", "kind": "add optional properties", "detail": "detail (object), params (object), inputs (array)",
     "evidence": "metric_value table / MetricsService output; Stage 16 DC-02 (detail); Stage 23 DW-16 scenario"},
    {"schema": "partner-feed-envelope", "ic": "IC-7", "kind": "add optional property", "detail": "ingest_ts (timestamp string) - a column of the legacy partner_feed row",
     "evidence": "Stage 23 DW-16: 8,567 of 8,567 shipped partner_feed rows carry ingest_ts and failed v0.1 (additionalProperties false)"},
    {"schema": "error-envelope", "ic": "IC-7", "kind": "widen", "detail": "error.details may be null (the envelope of an error raised without details, e.g. E-HUB-INTERNAL)",
     "evidence": "hub.web.wire.envelope(HubError()) emits details: null; Stage 23 DW-16"},
    {"schema": "hub-config", "ic": "IC-3", "kind": "rewrite as the EFFECTIVE configuration",
     "detail": "describes the configuration after every settings resolver applied its defaults: adds hub, runtime, capability_authority, approval_refs, auth, workflow, facts, case_creation, runs.*, site, search, templates, gateway, network.tls, audit.*; required keys unchanged "
               "(zone_h, disposition, closure, schedule, data_origin); the raw operator file need not carry the required keys because defaults fill them",
     "evidence": "IC-3 key table (docs/17-implementation-prd/implementation-prd.md IP-5); Stage 23 DW-16 builds the effective configuration with the real resolvers"},
]


def load(name):
    with open(os.path.join(SRC, name + ".schema.json"), encoding="utf-8") as f:
        return json.load(f)


def derive(name, doc):
    d = copy.deepcopy(doc)
    p = d.get("properties", {})
    if name == "intake-outcome":
        p["contract_missing"] = {"type": "array", "items": {"type": "string"}}
        p["conflicts_with"] = STR_OR_NULL
        p["reason_detail"] = {"type": "object"}
    elif name == "metric-value":
        p["detail"] = {"type": "object"}
        p["params"] = {"type": "object"}
        p["inputs"] = {"type": "array"}
    elif name == "partner-feed-envelope":
        p["ingest_ts"] = copy.deepcopy(TS)
    elif name == "error-envelope":
        p["error"]["properties"]["details"] = {"type": ["object", "null"]}
    elif name == "hub-config":
        props = dict((k, v) for k, v in HUB_CONFIG_PROPS.items() if v is not None)
        props["contract_bindings"] = p["contract_bindings"]
        d["properties"] = props
        d["description"] = "Effective hub configuration (defaults applied) (Stage 12 v0.2 addendum; synthetic, unvalidated)"
    d["$id"] = doc["$id"] + ":v0.2"
    if name != "hub-config":
        d["description"] = doc.get("description", "").replace("Stage 12 v0.1 DRAFT", "Stage 12 v0.2 addendum, derived from v0.1 DRAFT")
    return d


def main():
    os.makedirs(DST, exist_ok=True)
    names = sorted(os.path.basename(p)[:-len(".schema.json")] for p in glob.glob(os.path.join(SRC, "*.schema.json")))
    for n in names:
        with open(os.path.join(DST, n + ".schema.json"), "w", encoding="utf-8") as f:
            json.dump(derive(n, load(n)), f, indent=2)
            f.write("\n")
    with open(os.path.join(REPO, "docs", "23-human-control", "stage12-v0.2", "schema-addendum-changes.json"), "w", encoding="utf-8") as f:
        json.dump({"schema": "stage12-v0.2-schema-changes/v1", "label": "synthetic, unvalidated", "source": "docs/12-specs/contracts/schemas (v0.1, frozen)",
                   "schemas": names, "changes": CHANGES}, f, indent=2)
        f.write("\n")
    print("wrote %d schemas" % len(names))


if __name__ == "__main__":
    main()

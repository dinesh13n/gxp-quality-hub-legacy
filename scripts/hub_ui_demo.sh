#!/usr/bin/env sh
# Build a populated reviewer-UI sandbox and serve it on 127.0.0.1:8081 (synthetic, unvalidated).
# Usage: sh scripts/hub_ui_demo.sh SANDBOX_DIR BASELINE_DB
#   SANDBOX_DIR  absolute, short path OUTSIDE this git tree (e.g. C:/hub-sandbox); Windows paths over 260 chars break backups
#   BASELINE_DB  the shipped 125-case legacy.sqlite3 (pinned sha256 c254649f...), e.g. a backup taken before any `app.generate --reset`
# Demo logins (password = env var or default): alice/reviewer, carol/quality_lead, bob/dispositioner.
# Disposition stays refused (E-GATE-NO-HOLDERS) until zone_h.holders is set with a recorded approval_refs entry (OD-S12-06, HAR-11).
set -eu
S=${1:?SANDBOX_DIR required}; BASE=${2:?BASELINE_DB required}
C=$S/hub-config.json; D=$S/hubdata; B=$S/hubbak; L=$S/L; R=$S/runs
[ -e "$D" ] && { echo "$D already exists; choose a new SANDBOX_DIR" >&2; exit 1; }
mkdir -p "$S/anchor" "$D" "$B" "$L" "$R"
echo "{\"audit\":{\"anchor_path\":\"$S/anchor/audit-anchor.jsonl\",\"anchor_every\":100}}" > "$C"

# Sandbox copy of the legacy estate with the pinned baseline DB (the repo copy is never modified)
tar --exclude=.git --exclude=__pycache__ -cf - . | tar -xf - -C "$L"
cp "$BASE" "$L/data/legacy.sqlite3"

for m in admin policy decision intake runs web; do
  python -m hub.$m --config "$C" migrate --data-dir "$D" --backup-root "$B" >/dev/null
done
python -m hub.policy --config "$C" seed --data-dir "$D" >/dev/null
python -m hub.policy --config "$C" load-as-found --data-dir "$D" --legacy-root "$L" --run-dir "$R/policy" >/dev/null
python -m hub.intake --config "$C" ingest-legacy --data-dir "$D" --legacy-root "$L" --run-dir "$R/intake" --csv-tier tiny >/dev/null
python -m hub.decision --config "$C" backfill --data-dir "$D" --legacy-root "$L" --run-dir "$R/backfill" >/dev/null
python -m hub.decision --config "$C" crosswalk-run --data-dir "$D" --legacy-root "$L" --run-dir "$R/crosswalk" >/dev/null
for f in PRIORITY MANUAL_REVIEW; do
  python -m hub.web --config "$C" produce-traces --data-dir "$D" --legacy-root "$L" --function $f --ruleset-ref as-found-python@1 >/dev/null
done

HUB_NEW_USER_PASSWORD=${ALICE_PASSWORD:-Reviewer-Demo-2026!} python -m hub.admin --config "$C" user create --data-dir "$D" --principal alice --role reviewer >/dev/null
HUB_NEW_USER_PASSWORD=${CAROL_PASSWORD:-Lead-Demo-2026!} python -m hub.admin --config "$C" user create --data-dir "$D" --principal carol --role quality_lead >/dev/null
HUB_NEW_USER_PASSWORD=${BOB_PASSWORD:-Dispo-Demo-2026!} python -m hub.admin --config "$C" user create --data-dir "$D" --principal bob --role dispositioner >/dev/null

echo "Ready: open http://127.0.0.1:8081/ui/login (Ctrl+C to stop)"
exec python -m hub.web --config "$C" serve --data-dir "$D" --port 8081

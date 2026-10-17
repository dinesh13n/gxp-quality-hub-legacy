#!/usr/bin/env sh
set -eu
if [ ! -f "${LEGACY_DB:-data/legacy.sqlite3}" ]; then
  python -m app.generate --count 6000 --seed 4326
fi
exec python -m app.server

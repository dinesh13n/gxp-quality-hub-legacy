#!/usr/bin/env sh
set -eu
python -m app.workshop_check
python -m unittest discover -s tests -v
python scripts/smoke.py

# Rollback
1. Flag off: `ai.enabled=false` (default) or turn on `hub.kill`. Both refuse before any socket is opened.
2. Clear the four env vars from your session.
3. Delete nothing: code, config placeholders, docs and audit entries stay. Audit entries are append-only by design.
4. Full revert, if ever wanted, is a git revert of the stage-44 commits; the default state is already identical to before.

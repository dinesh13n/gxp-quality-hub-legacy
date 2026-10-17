# Archived enterprise interface notes — Pharma Quality

The legacy data landscape includes a standalone operational database `data/enterprise_legacy.sqlite3` and older transactional/partner systems. The nightly reconciliation script in `legacy_batch/` reads this historical database directly. It predates the HTTP integration bridge and duplicates some approval logic.

The 12 tables include organizations, operational objects, state history, document links, evidence events, policy register, cross references, workflow tasks, financial adjustments, integration attempts, access audit, and retention events.

This documentation reflects a historic design, not a guaranteed up-to-date system of record. The regional policy register has overlapping active and historical intervals. Data is synthetic. Operational reports should not be used as automated release, treatment, switching, or lending decisions.

# Pharma — source-system landscape

Local database tables reflect a simplified integration of operational systems rather than a canonical enterprise data model.

| System | Data pattern | Typical coordination issue |
|---|---|---|
| Transaction application | SQLite transactional records | state/approval workflow drift |
| Source partner gateway | queued JSON payloads, v1/v2 | delayed, duplicated or missing references |
| Domain source | relational entity/detail/auxiliary tables | effective date and reconciliation issues |
| Document archive | JSONL extracted documents | inconsistent confidence, mixed locale, untrusted text |
| Operational finance | monthly cost table | mismatched reporting windows |

No real corporate systems or credentials are included.

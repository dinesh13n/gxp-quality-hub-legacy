# Service interfaces and business ownership — Pharma Quality

- Legacy API: synchronous CRUD and reporting.
- Source gateway: independent HTTP adapter serving upstream records.
- Ingestion bridge: replay and checkpoint-based ingestion.
- Night-shift reconciliation: separate historical batch processor reading an enterprise SQLite file directly.
- Java reconciliation: runs through the archived JVM component.
- JavaScript policy consumer: applies a distinct historical rule interpretation.

Operations, legal/compliance, IT and domain quality teams have not agreed on a canonical definition for every state. Older escalation emails and policy revisions are retained in `data/archive_documents`.

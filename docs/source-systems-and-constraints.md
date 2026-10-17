# Systems, contracts and operating constraints

**ElectronicBatchRecord** publishes OOS_RESULT, DEVIATION, CAPA_UPDATE messages. **LIMS-QMS** supplies competing facts and effective-dated master data. Partner files can be replayed and have schema revisions 1.0, 1.1, 2.0, and unsupported variants.

The business manages TABLET, STERILE_VIAL, API, BIOLOGIC; human queues track OPEN, INVESTIGATING, QA_REVIEW, DISPOSITIONED, REOPENED. Source timestamps, ingestion timestamps and revision dates are distinct.

Process maps and terminology are not fully agreed across teams. No assumption is made that AI is appropriate for any particular processing step.

Synthetic evidence includes policy exceptions and upstream outages; some records disagree. Historic incidents and operational practice must be cross-checked before proposing changes.

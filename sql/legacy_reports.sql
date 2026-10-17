-- Untuned monthly legacy reporting: joins without a date restriction; financial figures are floats.
SELECT c.region, c.status, count(DISTINCT c.id) as cases, sum(c.amount) as gross_amount
FROM cases c LEFT JOIN events e ON e.case_id=c.id
GROUP BY c.region,c.status ORDER BY gross_amount DESC;
-- Domain-specific reconciliation focuses on source records; see docs/domain-contracts.md.
SELECT message_kind, tenant, COUNT(*) AS rows_received FROM vendor_file_rows GROUP BY message_kind,tenant;

// Starter queries for FalkorDB Browser (http://localhost:3000, graph: gxp_quality). Synthetic, unvalidated data.

// 1. Schema overview: one row per relationship type
MATCH (a)-[e]->(b) RETURN labels(a)[0] AS from, type(e) AS rel, labels(b)[0] AS to, count(*) AS n ORDER BY n DESC

// 2. Quality chain for one batch: material, site, lab results, deviations and their CAPAs
MATCH p = (b:Batch {id: 'BT00000000'})-[*1..2]-() RETURN p

// 3. Critical deviations with overdue CAPAs, and where they were made
MATCH (s:Site)<-[:MADE_AT]-(b:Batch)-[:HAS_DEVIATION]->(d:Deviation {classification: 'CRITICAL'})-[:HAS_CAPA]->(c:CAPA {state: 'OVERDUE'})
RETURN s, b, d, c

// 4. Everything at one site (cases, batches, materials)
MATCH p = (:Site {id: 'IN-BLR'})<-[]-() RETURN p LIMIT 150

// 5. A case and its event history
MATCH p = (:Case {id: 'C00000001'})-[*1]-() RETURN p

// 6. High-severity open cases per site
MATCH (c:Case {severity: 'HIGH'})-[:AT_SITE]->(s:Site) WHERE c.status <> 'CLOSED' RETURN s.id AS site, count(c) AS open_high ORDER BY open_high DESC

// 7. Enterprise: related objects with their organisations. Every source link is an untyped 'relates_to' and every object
//    has at most one, so the 4,166 links are isolated pairs (no chains).
MATCH p = (oa:Organization)<-[:BELONGS_TO]-(a:OperationalObject)-[:RELATES_TO]->(b:OperationalObject)-[:BELONGS_TO]->(ob:Organization)
RETURN p LIMIT 25

// 8. Enterprise: organisations with the most cross-referenced objects
MATCH (o:Organization)<-[:BELONGS_TO]-(x:OperationalObject)-[:RELATES_TO]-() RETURN o.name, count(DISTINCT x) AS linked ORDER BY linked DESC LIMIT 10

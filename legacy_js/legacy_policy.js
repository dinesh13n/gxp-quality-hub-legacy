// Legacy front-end approval thresholds. These do not consistently agree with server policy.
const fs = require('fs');
const policies = JSON.parse(fs.readFileSync('contracts/decision-policies-archive.json', 'utf8'));
function threshold(region,year) { const r=policies.historical_versions.find(p=>p.region===region && p.effective_from.startsWith(String(year))); return r ? r.limit : 999999; }
function legacyAllows(amount,region,year) { return Number(amount) <= threshold(region,year)*1.05; }
if(require.main===module) console.log(JSON.stringify({domain:"Pharma batch deviation and CAPA",threshold:threshold('APAC',2026),example:legacyAllows(27000,'APAC',2026)}));
module.exports={threshold,legacyAllows};

"""Lightweight knowledge-graph exports for demos (synthetic, unvalidated). Standard library only; no FalkorDB needed.

  python -m graph.export [--out exports/knowledge-graph] [--no-enterprise] [--html-enterprise-pairs 100]

Writes to --out:
  knowledge-graph.html     single-file interactive viewer (quality graph + a sample of enterprise pairs); open in a browser
  knowledge-graph.json     node-link JSON {nodes, links} (D3, Cytoscape.js, NetworkX node_link_graph)
  knowledge-graph.graphml  GraphML (Gephi, yEd, Cytoscape desktop)
  nodes.csv, edges.csv     flat tables (spreadsheets, bulk loaders)
Node keys are "<Label>:<id>". Source databases are opened read-only; free text is not projected (see graph.model).
"""
import argparse
import csv
import json
import os
from xml.sax.saxutils import escape, quoteattr

from graph import model

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUALITY_LABELS = ("Site", "Material", "Batch", "LabResult", "Deviation", "CAPA", "Case", "Account", "CaseEvent")
COLORS = {"Site": "#d62728", "Material": "#9467bd", "Batch": "#1f77b4", "LabResult": "#17becf", "Deviation": "#ff7f0e",
          "CAPA": "#e377c2", "Case": "#2ca02c", "Account": "#8c564b", "CaseEvent": "#bcbd22",
          "OperationalObject": "#7f7f7f", "Organization": "#393b79"}


def node_link(g, labels=None, keep=None):
    """{nodes, links} restricted to `labels` and/or an explicit set of node keys `keep`."""
    def ok(label, nid):
        return (labels is None or label in labels) and (keep is None or (label, nid) in keep)
    nodes = [dict(key="%s:%s" % (label, nid), label=label, id=nid, **props)
             for label, items in sorted(g.nodes.items()) for nid, props in sorted(items.items()) if ok(label, nid)]
    links = [dict(source="%s:%s" % (sl, s), target="%s:%s" % (dl, d), type=t, **p)
             for (t, sl, dl), items in sorted(g.edges.items()) for s, d, p in items if ok(sl, s) and ok(dl, d)]
    return {"nodes": nodes, "links": links}


def enterprise_sample(g, pairs):
    """The first `pairs` RELATES_TO links with both objects and their organisations."""
    keep = set()
    belongs = {s: d for s, d, _ in g.edges.get(("BELONGS_TO", "OperationalObject", "Organization"), [])}
    for s, d, _ in g.edges.get(("RELATES_TO", "OperationalObject", "OperationalObject"), [])[:pairs]:
        for o in (s, d):
            keep.add(("OperationalObject", o))
            if o in belongs:
                keep.add(("Organization", belongs[o]))
    return keep


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)


def _gml_type(values):
    if all(isinstance(v, bool) for v in values):
        return "boolean"
    if all(isinstance(v, int) and not isinstance(v, bool) for v in values):
        return "long"
    if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in values):
        return "double"
    return "string"


def write_graphml(path, data):
    def keys(items, skip):
        vals = {}
        for it in items:
            for k, v in it.items():
                if k not in skip:
                    vals.setdefault(k, []).append(v)
        return {k: _gml_type(v) for k, v in sorted(vals.items())}
    nkeys, ekeys = keys(data["nodes"], {"key"}), keys(data["links"], {"source", "target"})
    with open(path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<graphml xmlns="http://graphml.graphdrawing.org/xmlns">\n')
        for k, t in nkeys.items():
            f.write('  <key id="n_%s" for="node" attr.name=%s attr.type="%s"/>\n' % (k, quoteattr(k), t))
        for k, t in ekeys.items():
            f.write('  <key id="e_%s" for="edge" attr.name=%s attr.type="%s"/>\n' % (k, quoteattr(k), t))
        f.write('  <graph id="gxp_quality" edgedefault="directed">\n')
        for n in data["nodes"]:
            f.write("    <node id=%s>" % quoteattr(n["key"]))
            f.write("".join('<data key="n_%s">%s</data>' % (k, escape(str(v))) for k, v in n.items() if k != "key"))
            f.write("</node>\n")
        for i, e in enumerate(data["links"]):
            f.write('    <edge id="e%d" source=%s target=%s>' % (i, quoteattr(e["source"]), quoteattr(e["target"])))
            f.write("".join('<data key="e_%s">%s</data>' % (k, escape(str(v))) for k, v in e.items() if k not in ("source", "target")))
            f.write("</edge>\n")
        f.write("  </graph>\n</graphml>\n")


def write_csv(path, rows, first):
    cols = list(first) + sorted({k for r in rows for k in r} - set(first))
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>GxP Knowledge Graph</title>
<script src="https://unpkg.com/vis-network@9.1.9/standalone/umd/vis-network.min.js"></script>
<style>
:root{--bg:#fafafa;--fg:#1b1b1b;--panel:#fff;--line:#ddd;--muted:#666}
@media (prefers-color-scheme:dark){:root{--bg:#15181c;--fg:#e8e8e8;--panel:#1e2228;--line:#333;--muted:#9aa}}
*{box-sizing:border-box}body{margin:0;font:14px/1.4 system-ui,sans-serif;background:var(--bg);color:var(--fg);display:flex;height:100vh}
aside{width:300px;max-width:42vw;padding:12px 14px;border-right:1px solid var(--line);background:var(--panel);overflow:auto}
h1{font-size:16px;margin:0 0 4px}.sub{color:var(--muted);font-size:12px;margin-bottom:10px}
label.f{display:flex;align-items:center;gap:6px;margin:3px 0;cursor:pointer}.sw{width:12px;height:12px;border-radius:50%;display:inline-block}
input[type=search]{width:100%;padding:6px;margin:8px 0;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:4px}
#graph{flex:1;min-width:0}#props{font-size:12px;word-break:break-word}#props table{border-collapse:collapse;width:100%}
#props td{border-top:1px solid var(--line);padding:3px 4px;vertical-align:top}#props td:first-child{color:var(--muted);width:40%}
.count{color:var(--muted);margin-left:auto;font-size:12px}button{margin-top:6px;padding:4px 8px}
@media (max-width:640px){body{flex-direction:column}aside{width:100%;max-width:none;height:40vh;border-right:0;border-bottom:1px solid var(--line)}}
</style></head><body>
<aside>
<h1>GxP Knowledge Graph</h1><div class="sub">Synthetic, unvalidated legacy data. __SUMMARY__</div>
<input id="q" type="search" placeholder="Find node id (e.g. BT00000000, IN-BLR)">
<div id="filters"></div><button id="fit">Fit view</button>
<h1 style="margin-top:14px">Selection</h1><div id="props" class="sub">Click a node or edge.</div>
</aside>
<div id="graph"></div>
<script id="data" type="application/json">__DATA__</script>
<script>
const D=JSON.parse(document.getElementById('data').textContent), C=__COLORS__;
const nodes=new vis.DataSet(D.nodes.map(n=>({id:n.key,label:n.label==='CaseEvent'||n.label==='LabResult'?'':n.id,raw:n,
  title:n.label+' '+n.id,color:C[n.label]||'#888',shape:'dot',size:{Site:22,Organization:16,Material:12,Batch:11,Case:11,Deviation:10,CAPA:9}[n.label]||6,
  font:{size:10,color:getComputedStyle(document.body).color}})));
const edges=new vis.DataSet(D.links.map((e,i)=>({id:i,from:e.source,to:e.target,label:'',title:e.type,raw:e,arrows:{to:{enabled:true,scaleFactor:.4}},
  color:{color:'#9999',highlight:'#555'},width:.6})));
const net=new vis.Network(document.getElementById('graph'),{nodes,edges},{physics:{solver:'forceAtlas2Based',stabilization:{iterations:250}},
  interaction:{hover:true,tooltipDelay:120}});
net.once('stabilizationIterationsDone',()=>net.setOptions({physics:false}));
const hidden=new Set(), counts={};D.nodes.forEach(n=>counts[n.label]=(counts[n.label]||0)+1);
const F=document.getElementById('filters');
Object.keys(counts).sort().forEach(l=>{const w=document.createElement('label');w.className='f';
  w.innerHTML='<input type="checkbox" checked><span class="sw" style="background:'+(C[l]||'#888')+'"></span>'+l+'<span class="count">'+counts[l]+'</span>';
  w.querySelector('input').onchange=ev=>{ev.target.checked?hidden.delete(l):hidden.add(l);
    nodes.update(D.nodes.filter(n=>n.label===l).map(n=>({id:n.key,hidden:hidden.has(l)})));};F.appendChild(w);});
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const show=o=>{document.getElementById('props').innerHTML='<table>'+Object.entries(o).map(([k,v])=>'<tr><td>'+esc(k)+'</td><td>'+esc(v)+'</td></tr>').join('')+'</table>';};
net.on('click',p=>{if(p.nodes.length)show(nodes.get(p.nodes[0]).raw);else if(p.edges.length)show(edges.get(p.edges[0]).raw);});
document.getElementById('q').onkeydown=ev=>{if(ev.key!=='Enter')return;const v=ev.target.value.trim().toLowerCase();
  const hit=D.nodes.find(n=>n.id.toLowerCase()===v)||D.nodes.find(n=>n.id.toLowerCase().includes(v));
  if(hit){net.selectNodes([hit.key]);net.focus(hit.key,{scale:1.6,animation:true});show(hit);}};
document.getElementById('fit').onclick=()=>net.fit({animation:true});
</script></body></html>
"""


def write_html(path, data, summary):
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    page = HTML.replace("__DATA__", blob).replace("__COLORS__", json.dumps(COLORS)).replace("__SUMMARY__", escape(summary))
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m graph.export", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--legacy-db", default=os.environ.get("LEGACY_DB", os.path.join(ROOT, "data", "legacy.sqlite3")))
    ap.add_argument("--enterprise-db", default=os.path.join(ROOT, "data", "enterprise_legacy.sqlite3"))
    ap.add_argument("--no-enterprise", action="store_true")
    ap.add_argument("--html-enterprise-pairs", type=int, default=100, help="enterprise RELATES_TO pairs shown in the HTML viewer")
    ap.add_argument("--out", default=os.path.join(ROOT, "exports", "knowledge-graph"))
    a = ap.parse_args(argv)
    g = model.build(a.legacy_db, None if a.no_enterprise else a.enterprise_db)
    os.makedirs(a.out, exist_ok=True)
    full = node_link(g)
    write_json(os.path.join(a.out, "knowledge-graph.json"), full)
    write_graphml(os.path.join(a.out, "knowledge-graph.graphml"), full)
    write_csv(os.path.join(a.out, "nodes.csv"), full["nodes"], ("key", "label", "id"))
    write_csv(os.path.join(a.out, "edges.csv"), full["links"], ("source", "target", "type"))
    view = node_link(g, labels=QUALITY_LABELS)
    if not a.no_enterprise and a.html_enterprise_pairs > 0:
        extra = node_link(g, keep=enterprise_sample(g, a.html_enterprise_pairs))
        view = {"nodes": view["nodes"] + extra["nodes"], "links": view["links"] + extra["links"]}
    summary = "Viewer: %d nodes, %d edges (full export: %d / %d)." % (len(view["nodes"]), len(view["links"]), len(full["nodes"]), len(full["links"]))
    write_html(os.path.join(a.out, "knowledge-graph.html"), view, summary)
    print("full graph: %d nodes, %d edges -> %s" % (len(full["nodes"]), len(full["links"]), a.out))
    print(summary)
    for fn in sorted(os.listdir(a.out)):
        print("  %-26s %8.1f KB" % (fn, os.path.getsize(os.path.join(a.out, fn)) / 1024))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Stage 7 stdlib-only static analysis (no third-party analyzers installed on device). Read-only on source."""
import ast,sys,os,json,re,hashlib,collections
ROOT=sys.argv[1]
files=[]
for dp,dn,fn in os.walk(ROOT):
    dn[:]=[d for d in dn if d not in('.git','data','docs','.fde','__pycache__')]
    for f in fn:
        if f.endswith('.py'):files.append(os.path.relpath(os.path.join(dp,f),ROOT))
files.sort()
class CC(ast.NodeVisitor):
    def __init__(s):s.n=1
    def generic_visit(s,node):
        if isinstance(node,(ast.If,ast.For,ast.While,ast.ExceptHandler,ast.With,ast.IfExp,ast.comprehension,ast.Assert)):s.n+=1
        if isinstance(node,ast.BoolOp):s.n+=len(node.values)-1
        super().generic_visit(node)
out={'files':{},'internal_imports':{},'findings':collections.defaultdict(list)}
allnorm=[]
mods={f[:-3].replace('/','.').replace('.__init__',''):f for f in files}
for f in files:
    src=open(os.path.join(ROOT,f),encoding='utf8').read();lines=src.splitlines();t=ast.parse(src)
    funcs=[]
    for n in ast.walk(t):
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
            c=CC();c.visit(n);funcs.append({'name':n.name,'line':n.lineno,'end':n.end_lineno,'loc':n.end_lineno-n.lineno+1,'cc':c.n,'has_docstring':ast.get_docstring(n) is not None,'annotated':bool(n.returns or any(a.annotation for a in n.args.args))})
    mod_cc=CC();mod_cc.visit(t)
    semis=sum(1 for l in lines if re.search(r';\s*\S',re.sub(r"'[^']*'|\"[^\"]*\"",'',l)) and not l.strip().startswith('#'))
    out['files'][f]={'lines':len(lines),'non_blank':sum(1 for l in lines if l.strip()),'max_line_len':max((len(l) for l in lines),default=0),'lines_gt_160':sum(len(l)>160 for l in lines),'lines_with_semicolon_statements':semis,'functions':len(funcs),'max_func_cc':max((x['cc'] for x in funcs),default=0),'module_cc':mod_cc.n,'funcs_with_docstring':sum(x['has_docstring'] for x in funcs),'funcs_annotated':sum(x['annotated'] for x in funcs),'module_docstring':ast.get_docstring(t) is not None,'top_funcs':sorted(funcs,key=lambda x:-x['cc'])[:3],'indent_style':'1-space' if any(re.match(r'^ \S',l) for l in lines) else '4-space/none'}
    imps=set()
    for n in ast.walk(t):
        if isinstance(n,ast.ImportFrom):
            m=n.module or '';
            if n.level:
                base=f.rsplit('/',1)[0].replace('/','.') if '/' in f else ''
                m=(base+'.'+m).strip('.') if m else base
            imps.add(m)
        elif isinstance(n,ast.Import):
            for a in n.names:imps.add(a.name)
    out['internal_imports'][f]=sorted(i for i in imps if i.split('.')[0] in {'app','services','legacy_batch','tests'} or i in mods)
    # security / quality greps (AST-aware where practical)
    for n in ast.walk(t):
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in('execute','executemany','executescript') and n.args:
            a=n.args[0]
            if isinstance(a,ast.BinOp) or (isinstance(a,ast.Call) and isinstance(a.func,ast.Attribute) and a.func.attr=='format') or isinstance(a,ast.JoinedStr):
                out['findings']['sql_string_building'].append(f'{f}:{n.lineno}')
        if isinstance(n,ast.ExceptHandler) and (n.type is None or (isinstance(n.type,ast.Name) and n.type.id=='Exception')):
            out['findings']['broad_except'].append(f'{f}:{n.lineno}')
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='urlopen':out['findings']['urlopen_no_scheme_check'].append(f'{f}:{n.lineno}')
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in('unlink','rmtree','remove'):out['findings']['file_deletion'].append(f'{f}:{n.lineno}')
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='Popen' or (isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='run' and getattr(n.func.value,'id','')=='subprocess'):out['findings']['subprocess_use'].append(f'{f}:{n.lineno}')
    for i,l in enumerate(lines,1):
        if re.search(r"['\"]0\.0\.0\.0['\"]",l):out['findings']['bind_all_interfaces'].append(f'{f}:{i}')
        if re.search(r'Path\(__file__\)\.resolve\(\)\.parents\[|ROOT\s*/\s*.data',l) and 'data' in src:pass
        if re.search(r'\bpassword\b|\bsecret\b|api[_-]?key|token',l,re.I):out['findings']['secret_like_words'].append(f'{f}:{i}')
    for i in range(len(lines)):
        w=[re.sub(r'\s+','',x) for x in lines[i:i+6]]
        if all(len(x)>25 for x in w):allnorm.append((hashlib.md5('|'.join(w).encode()).hexdigest(),f,i+1))
d=collections.defaultdict(list)
for h,f,i in allnorm:d[h].append(f'{f}:{i}')
out['duplicate_6line_windows']=[v for v in d.values() if len({x.split(':')[0] for x in v})>1 or len(v)>1][:20]
# server handler duplication measured specifically: identical-looking pagination blocks
out['pagination_clamp_copies']=sum(open(os.path.join(ROOT,f),encoding='utf8').read().count("min(100,int(q.get('limit'") for f in files)
out['findings']=dict(out['findings'])
out['totals']={'py_files':len(files),'py_lines':sum(v['lines'] for v in out['files'].values()),'functions':sum(v['functions'] for v in out['files'].values()),'funcs_with_docstring':sum(v['funcs_with_docstring'] for v in out['files'].values()),'funcs_annotated':sum(v['funcs_annotated'] for v in out['files'].values())}
json.dump(out,open(sys.argv[2],'w'),indent=1,sort_keys=True)
print(json.dumps(out['totals']))
for f,v in out['files'].items():print(f"{f:42} L={v['lines']:3} maxlen={v['max_line_len']:4} semis={v['lines_with_semicolon_statements']:3} funcs={v['functions']:2} maxCC={v['max_func_cc']:2} modCC={v['module_cc']:3} doc={v['funcs_with_docstring']} indent={v['indent_style']}")
print(json.dumps(out['findings'],indent=0)[:3500]);print(out['pagination_clamp_copies']);print(out['duplicate_6line_windows'][:5])
print(json.dumps(out['internal_imports'],indent=0))

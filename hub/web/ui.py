"""Server-rendered reviewer pages (ADR-014 option B; INC-08). No JavaScript, no inline script or style (CSP default-src 'self'), no external asset.

Every dynamic string goes through html.escape (quote=True): untrusted source text is escaped AND labelled. Forms carry a derived csrf_token. The
disposition form has NO pre-selected decision or action (AC-GATE-10): the human must choose. A page is a thin view of the same services the API uses;
it never decides anything itself and it has no route that skips the Zone H choke point (hub.gate.actions).
"""
import html
import json

from hub.core.errors import HubError
from hub.gate import pack as gpack
from hub.gate import reauth
from hub.gate.actions import ZoneHActions
from hub.web import csrf
from hub.web.api import authn, cookie, dec, disp, rev
from hub.web.app import Response
from hub.web.tokens import CompositeAuthenticator  # noqa: F401

CSS = ("body{font:15px/1.4 system-ui,sans-serif;margin:0;color:#1b1b1b;background:#fafafa}header{background:#243447;color:#fff;padding:.6rem 1rem}"
       "header a{color:#cfe3ff;margin-right:1rem}main{padding:1rem;max-width:72rem}.banner{background:#fff3cd;padding:.4rem 1rem;font-size:.85rem}"
       "table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccc;padding:.3rem .5rem;text-align:left;vertical-align:top}"
       ".err{background:#f8d7da;padding:.5rem;border:1px solid #d99}.ok{background:#d4edda;padding:.5rem;border:1px solid #9c9}"
       "pre{background:#eee;padding:.5rem;overflow:auto;white-space:pre-wrap}label{display:block;margin:.4rem 0 .1rem}"
       "input[type=text],input[type=password],textarea,select{width:32rem;max-width:100%}.untrusted{color:#555;font-style:italic}\n")
LABEL = "synthetic, unvalidated"


def e(v):
    return html.escape("" if v is None else str(v), quote=True)


def page(title, body, sess=None, status=200, headers=None):
    nav = ""
    if sess is not None:
        nav = ('<a href="/ui/">Home</a><a href="/ui/queue">Exception queue</a>'
               '<form method="post" action="/ui/logout" style="display:inline"><input type="hidden" name="csrf_token" value="%s">'
               '<button type="submit">Log out (%s)</button></form>' % (e(csrf.csrf_token(sess)), e(sess.principal.principal_id)))
    doc = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
           '<title>%s</title><link rel="stylesheet" href="/ui/static/app.css"></head><body><header>GxP Quality Hub %s</header>'
           '<div class="banner">%s. Decision support only: a human decides.</div><main><h1>%s</h1>%s</main></body></html>'
           % (e(title), nav, LABEL, e(title), body))
    return Response(status, doc.encode("utf-8"), "text/html; charset=utf-8", headers)


def redirect(location, headers=None):
    return Response(303, b"", "text/plain", [("Location", location)] + list(headers or []))


def _err_page(ctx, err, back="/ui/"):
    st = getattr(err, "http", None) or 422
    return page("Request refused", '<p class="err"><strong>%s</strong>: %s</p><p><a href="%s">Back</a></p>' % (e(err.code), e(err.message), e(back)),
                ctx.sess, st)


def _form(action, ctx, inner, button):
    return ('<form method="post" action="%s"><input type="hidden" name="csrf_token" value="%s">%s<p><button type="submit">%s</button></p></form>'
            % (e(action), e(csrf.csrf_token(ctx.sess)), inner, e(button)))


def op_UI_STATIC(ctx):
    return Response(200, CSS.encode("utf-8"), "text/css; charset=utf-8")


def op_UI_LOGIN(ctx):
    return _login_page()


def _login_page(msg=None, status=200):
    inner = ('<p class="err">%s</p>' % e(msg)) if msg else ""
    inner += ('<form method="post" action="/ui/login"><label for="u">User</label><input id="u" type="text" name="username" autocomplete="username">'
              '<label for="p">Password</label><input id="p" type="password" name="password" autocomplete="current-password">'
              '<p><button type="submit">Log in</button></p></form>')
    return page("Log in", inner, None, status)


def op_UI_LOGIN_POST(ctx):
    a = authn(ctx)
    try:
        token = a.login(ctx.body.get("username", ""), ctx.body.get("password", ""), ctx.cid)
    except HubError as err:
        ctx.app.metrics.auth_failure("locked" if err.code == "E-AUTH-LOCKED" else "bad_credentials")
        return _login_page("Log in failed (%s)." % err.code, 401 if err.code != "E-AUTH-LOCKED" else 423)
    return redirect("/ui/", [cookie(token, ctx.s["auth"]["session_absolute_seconds"])])


def op_UI_LOGOUT(ctx):
    authn(ctx).logout(ctx.token, ctx.cid)
    return redirect("/ui/login", [cookie("", 0)])


def op_UI_HOME(ctx):
    roles = ctx.sess.principal.roles
    return page("Home", "<p>Signed in as %s (%s).</p><ul><li><a href=\"/ui/queue\">Exception queue</a></li></ul>"
                % (e(ctx.sess.principal.principal_id), e(", ".join(roles))), ctx.sess)


def op_UI_QUEUE(ctx):
    try:
        r = rev(ctx).queue(ctx.sess, ctx.q("queue"), ctx.q("reason"), ctx.q("source"), ctx.q("min_age_hours"), ctx.q("limit"), ctx.q("cursor"), ctx.cid)
    except HubError as err:
        return _err_page(ctx, err)
    rows = []
    for it in r["items"]:
        notes = it["notes"]
        n = ('<span class="untrusted">%s</span><br><small>%s</small>' % (notes["text_escaped"], e(notes["label"]))) if notes else ""
        case = ('<a href="/ui/cases/%s/trace">%s</a>' % (e(it["matched_case"]), e(it["matched_case"]))) if it["matched_case"] else ""
        rows.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                    % (e(it["raw_id"]), e(it["queue"]), e(it["primary_reason"]), e(it["source"]), e(it["age_hours"]), case, n))
    body = ("<p>%s item(s) in the queue. Nothing here is hidden; every item is shown once, oldest first.</p><table><tr><th>Item</th><th>Queue</th>"
            "<th>Reason</th><th>Source</th><th>Age (h)</th><th>Matched case</th><th>Source text (untrusted)</th></tr>%s</table>"
            % (e(r["total"]), "".join(rows)))
    if r.get("next"):
        body += '<p><a href="/ui/queue?cursor=%s">Next page</a></p>' % e(r["next"])
    return page("Exception queue", body, ctx.sess)


def op_UI_TRACE(ctx):
    cid = ctx.params["case_id"]
    try:
        r = rev(ctx).explanations(ctx.sess, cid, ctx.cid)
    except HubError as err:
        return _err_page(ctx, err)
    parts = []
    can_override = any(x in ctx.sess.principal.roles for x in ("reviewer", "quality_lead", "compliance"))
    for x in r["explanations"]:
        form = ""
        if can_override and x["flag_status"] == "open":
            form = _form("/ui/flags/%s/override" % x["flag_id"], ctx,
                         '<label for="a%s">Action</label><select id="a%s" name="action"><option value="">(choose)</option>'
                         '<option value="override">override</option><option value="dismiss">dismiss</option><option value="refuse">refuse</option>'
                         '</select><label for="r%s">Reason (required)</label><textarea id="r%s" name="reason" rows="2"></textarea>'
                         % (e(x["trace_id"]), e(x["trace_id"]), e(x["trace_id"]), e(x["trace_id"])), "Record")
        parts.append('<section><h2>%s</h2><p>%s</p><p>Rule set: %s. Flag %s is %s.%s</p>%s</section>'
                     % (e(x["function"]), e(x["text"]), e(x["ruleset_ref"]), e(x["flag_id"]), e(x["flag_status"]),
                        " <strong>Defaulted result.</strong>" if x["defaulted"] else "", form))
    link = ('<p><a href="/ui/cases/%s/pack">Evidence pack (dispositioner)</a></p>' % e(cid)) if "dispositioner" in ctx.sess.principal.roles else ""
    return page("Rule explanations for %s" % cid, "".join(parts) or "<p>No stored explanation.</p>" + link, ctx.sess)


def op_UI_OVERRIDE(ctx):
    fid = ctx.params["flag_id"]
    try:
        disp(ctx).act_on_flag(ctx.sess, fid, ctx.body.get("action", ""), ctx.body.get("reason", ""), ctx.body.get("replacement") or None, ctx.cid)
    except HubError as err:
        return _err_page(ctx, err)
    from hub.gate import flags
    case = flags.resolve(ctx.con, fid).get("case_id")
    return redirect("/ui/cases/%s/trace" % case if case else "/ui/queue")


def op_UI_PACK(ctx):
    cid = ctx.params["case_id"]
    try:
        if dec(ctx)._head(cid) is None:
            from hub.decision.errors import CaseNotFound
            raise CaseNotFound({"case_id": cid[:40]})
        pk = gpack.build(ctx.con, cid)
        m = disp(ctx).mode()
    except HubError as err:
        return _err_page(ctx, err)
    show = dict((k, v) for k, v in pk.items() if k != "pack_hash")
    body = "<p>Pack hash: <code>%s</code></p><pre>%s</pre>" % (e(pk["pack_hash"]), e(json.dumps(show, indent=2, sort_keys=True, ensure_ascii=True)))
    if m["mode"] == "none":
        body += "<p class=\"err\">Disposition mode is none: the hub records no disposition (E-GATE-MODE-NONE). Read-only.</p>"
    else:
        if m["mode"] == "event":
            opts = "".join('<option value="%s">%s</option>' % (e(v), e(v)) for v in m["values"])
            fields = ('<label for="d">Decision</label><select id="d" name="decision"><option value="">(choose)</option>%s</select>'
                      '<label for="b">Basis (required)</label><textarea id="b" name="basis" rows="3"></textarea>' % opts)
        else:
            fields = ('<label for="s">External system</label><input id="s" type="text" name="system"><label for="rf">Reference</label>'
                      '<input id="rf" type="text" name="reference">')
        fields = ('<label for="z">Action</label><select id="z" name="zh"><option value="">(choose)</option><option value="ZH-01">ZH-01 disposition</option>'
                  '<option value="ZH-02">ZH-02 QA release</option><option value="ZH-03">ZH-03 e-signature record</option></select>' + fields +
                  '<label for="st">Statement (ZH-03 only)</label><input id="st" type="text" name="statement">'
                  '<label for="ar">Authority reference (required)</label><input id="ar" type="text" name="authority_ref">'
                  '<label for="pw">Your password (step-up re-authentication)</label><input id="pw" type="password" name="password" autocomplete="off">'
                  '<input type="hidden" name="pack_hash" value="%s">' % e(pk["pack_hash"]))
        body += _form("/ui/cases/%s/disposition" % cid, ctx, fields, "Record my decision")
    return page("Evidence pack for %s" % cid, body, ctx.sess)


def op_UI_DISPOSITION(ctx):
    cid = ctx.params["case_id"]
    f = ctx.body
    try:
        a = authn(ctx)
        sess2 = a.reauthenticate(ctx.token, f.get("password", ""), ctx.cid)
        payload = dict((k, f[k]) for k in ("decision", "basis", "statement", "system", "reference") if f.get(k))
        req = {"action": f.get("zh", ""), "case_id": cid, "payload": payload, "pack_hash": f.get("pack_hash") or None,
               "authority_ref": f.get("authority_ref", ""), "reauth_token": reauth.token_for(sess2)}
        za = ZoneHActions(ctx.con, ctx.s, ctx.clock, ctx.anchor, ctx.app.d, ctx.app.disp, ctx.app.cfg)
        r = za.execute(sess2, req, ctx.cid)
    except HubError as err:
        return _err_page(ctx, err, "/ui/cases/%s/pack" % cid)
    return page("Decision recorded", '<p class="ok">Recorded %s as %s (audit %s). The decision is yours; the hub only stored it.</p>'
                % (e(r["action"]), e(r["event_ref"]), e(r["audit_seq"])), ctx.sess, 201)

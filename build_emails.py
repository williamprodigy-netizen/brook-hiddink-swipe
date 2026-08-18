#!/usr/bin/env python3
"""Brook Hiddink — the captured email sequence, as an inbox you can read.

78 emails pulled off his live list (19 Feb -> 6 Apr 2026), every one with the
real rendered screenshot. Left pane is the inbox, right pane is the email as it
actually landed. Toggle to plain text, or pop the original HTML.

Run:  python3 build_emails.py   ->  emails.html  (+ media/emails/*)
"""
import html as htmllib
import json, os, re, shutil, zipfile
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.expanduser("~/UNDERGROUND_FUNNELS_SSOT/02_EMAILS/_unattributed")
OUT_MEDIA = os.path.join(HERE, "media", "emails")
CST = timezone(timedelta(hours=-5))  # CDT during this window

os.makedirs(OUT_MEDIA, exist_ok=True)

# every message from his sending domain
stems = sorted({f[:-len("__plain.txt")] for f in os.listdir(SRC)
                if f.endswith("__plain.txt")})
rows = []
for stem in stems:
    jf = os.path.join(SRC, stem + ".json")
    if not os.path.exists(jf):
        continue
    d = json.load(open(jf))
    if "invictadigital.io" not in (d.get("sender_email") or ""):
        continue
    png = os.path.join(SRC, stem + "__rendered.png")
    raw = os.path.join(SRC, stem + "__raw.html")
    if not os.path.exists(png):
        continue
    slug = re.sub(r"[^A-Za-z0-9]+", "-", stem)[:90].strip("-")
    shutil.copy2(png, os.path.join(OUT_MEDIA, slug + ".png"))
    if os.path.exists(raw):
        shutil.copy2(raw, os.path.join(OUT_MEDIA, slug + ".html"))
    body = open(os.path.join(SRC, stem + "__plain.txt"),
                encoding="utf-8", errors="ignore").read()
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    dt = datetime.fromisoformat(d["received_utc"]).astimezone(CST)
    # gmail preview text arrives entity-encoded, and is sometimes blank
    preview = htmllib.unescape(d.get("preview_text") or "").strip()
    if len(preview) < 25:
        preview = " ".join(body.split("\n"))[:220]
    rows.append({
        "slug": slug,
        "subject": htmllib.unescape(d.get("subject") or "(no subject)"),
        "from": d.get("sender_name") or "",
        "email": d.get("sender_email") or "",
        "date": dt.strftime("%a %-d %b"),
        "time": dt.strftime("%-I:%M %p"),
        "iso": dt.strftime("%Y-%m-%d %H:%M"),
        "preview": preview[:220],
        "seq": d.get("likely_sequence_position"),
        "since": d.get("time_since_first_contact") or "",
        "body": body,
        "has_html": os.path.exists(raw),
        "golden": bool(re.search(r"golden ticket", body, re.I)),
    })

rows.sort(key=lambda r: r["iso"])
for i, r in enumerate(rows, 1):
    r["n"] = i

# a zip of the whole thing, for offline reading
zip_path = os.path.join(HERE, "brook-hiddink-emails.zip")
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for r in rows:
        base = f"{r['n']:02d} - {re.sub(r'[^A-Za-z0-9 ]+', '', r['subject'])[:60].strip()}"
        z.write(os.path.join(OUT_MEDIA, r["slug"] + ".png"), base + ".png")
        if r["has_html"]:
            z.write(os.path.join(OUT_MEDIA, r["slug"] + ".html"), base + ".html")

golden = [r["n"] for r in rows if r["golden"]]
first, last = rows[0]["date"], rows[-1]["date"]

NAV = ("<nav class=\"main\"><a href=\"index.html\">Overview</a>"
       "<a href=\"vsl.html\">The VSL</a><a href=\"webinar.html\">Webinar</a>"
       "<a href=\"emails.html\" class='on'>Emails</a><a href=\"sms.html\">SMS</a>"
       "<a href=\"transcripts.html\">Transcripts</a><a href=\"ads.html\">Ads</a>"
       "<a href=\"board.html\">Wired board</a></nav>")

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{--ink:#0f172a;--muted:#64748b;--line:#e2e8f0;--panel:#f8fafc;--bg:#eef0f3;
 --accent:#4f46e5;--gold:#b45309;--goldbg:#fffbeb}
body{background:var(--bg);color:var(--ink);
 font-family:Inter,system-ui,-apple-system,'Segoe UI',sans-serif;
 -webkit-font-smoothing:antialiased;line-height:1.55}
h1,h2,h3{font-weight:500;letter-spacing:-.02em}
a{color:inherit}
header.top{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:50}
.topin{max-width:1560px;margin:0 auto;padding:0 28px;display:flex;align-items:center;
 gap:26px;height:60px}
.brand{font-size:15px;font-weight:500;white-space:nowrap}
.brand span{color:var(--muted);font-weight:400}
nav.main{display:flex;gap:20px;overflow-x:auto;scrollbar-width:none}
nav.main::-webkit-scrollbar{display:none}
nav.main a{font-size:14px;color:var(--muted);text-decoration:none;white-space:nowrap;
 padding:6px 0;border-bottom:2px solid transparent}
nav.main a:hover{color:var(--ink)}
nav.main a.on{color:var(--ink);border-bottom-color:var(--accent)}
.wrap{max-width:1560px;margin:0 auto;padding:0 28px}
.hero{padding:38px 0 22px}
.kick{font-size:13px;letter-spacing:.11em;text-transform:uppercase;color:var(--muted);
 margin-bottom:11px}
.hero h1{font-size:40px;margin-bottom:12px}
.hero p{font-size:17px;color:#475569;max-width:900px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:13px;
 margin:24px 0 6px}
.tile{background:#fff;border:1px solid var(--line);border-radius:12px;padding:15px 17px}
.tile b{display:block;font-size:24px;font-weight:500;letter-spacing:-.03em}
.tile span{font-size:12px;color:var(--muted);display:block;margin-top:3px;line-height:1.4}
.bar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:20px 0 16px}
.btn{background:var(--ink);color:#fff;text-decoration:none;font-size:13.5px;
 padding:9px 15px;border-radius:9px;border:0;cursor:pointer;display:inline-block}
.btn.ghost{background:#fff;color:var(--ink);border:1px solid var(--line)}
.btn.ghost.on{border-color:var(--accent);color:var(--accent)}
#q{flex:1;min-width:220px;padding:9px 13px;border:1px solid var(--line);border-radius:9px;
 font-size:14px;background:#fff;color:var(--ink);font-family:inherit}
.split{display:grid;grid-template-columns:392px 1fr;gap:18px;padding-bottom:46px;
 align-items:start}
.inbox{background:#fff;border:1px solid var(--line);border-radius:14px;overflow:hidden;
 max-height:calc(100vh - 140px);overflow-y:auto;position:sticky;top:78px}
.row{padding:13px 15px;border-bottom:1px solid var(--line);cursor:pointer;display:block;
 width:100%;text-align:left;background:#fff;border-left:3px solid transparent;font:inherit}
.row:hover{background:var(--panel)}
.row.on{background:#eef2ff;border-left-color:var(--accent)}
.row .meta{display:flex;justify-content:space-between;gap:9px;
 font-size:11.5px;color:var(--muted);margin-bottom:3px;
 font-family:ui-monospace,Menlo,monospace}
.row .subj{font-size:14px;line-height:1.35;margin-bottom:3px;color:var(--ink)}
.row .prev{font-size:12px;color:var(--muted);line-height:1.4;
 display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.row.gold{background:var(--goldbg)}
.row.gold.on{background:#fef3c7}
.gt{display:inline-block;font-size:10px;letter-spacing:.08em;text-transform:uppercase;
 color:var(--gold);border:1px solid #fcd34d;background:#fffbeb;border-radius:4px;
 padding:1px 5px;margin-left:6px;vertical-align:1px}
.reader{background:#fff;border:1px solid var(--line);border-radius:14px;overflow:hidden}
.rhead{padding:20px 24px;border-bottom:1px solid var(--line)}
.rhead h2{font-size:22px;margin-bottom:8px;line-height:1.3}
.rhead .who{font-size:13.5px;color:#475569}
.rhead .who b{font-weight:500}
.rhead .stamp{font-size:12px;color:var(--muted);margin-top:5px;
 font-family:ui-monospace,Menlo,monospace}
.rtools{display:flex;gap:8px;padding:12px 24px;border-bottom:1px solid var(--line);
 background:var(--panel);flex-wrap:wrap}
.rbody{padding:0;background:var(--panel)}
.rbody img{display:block;width:100%;height:auto}
.plain{padding:28px 34px;background:#fff;white-space:pre-wrap;font-size:15px;
 line-height:1.75;color:#1e293b;max-width:74ch}
.hide{display:none}
.empty{padding:60px 24px;text-align:center;color:var(--muted);font-size:15px}
@media(max-width:1020px){.split{grid-template-columns:1fr}
 .inbox{position:static;max-height:420px}}
"""

def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))

items = []
for r in rows:
    items.append(
        f'<button class="row{" gold" if r["golden"] else ""}" data-i="{r["n"]}">'
        f'<div class="meta"><span>#{r["n"]:02d} &middot; {esc(r["from"])}</span>'
        f'<span>{esc(r["date"])} {esc(r["time"])}</span></div>'
        f'<div class="subj">{esc(r["subject"])}'
        f'{"<span class=gt>golden ticket</span>" if r["golden"] else ""}</div>'
        f'<div class="prev">{esc(r["preview"])}</div></button>')

data = json.dumps([{k: r[k] for k in
                    ("n", "slug", "subject", "from", "email", "date", "time",
                     "since", "seq", "body", "has_html", "golden")} for r in rows])

html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Emails — Brook Hiddink / High Ticket — Swipe</title><style>{CSS}</style></head>
<body>
<header class="top"><div class="topin"><div class="brand">Brook Hiddink
<span>&middot; High Ticket</span></div>{NAV}</div></header>
<div class="wrap">
<div class="hero"><div class="kick">Email sequence &middot; captured off his live list</div>
<h1>78 emails, {first} &rarr; {last} 2026</h1>
<p>Every email he sent a registrant who opted in, never bought, never booked. All from
<b>info@invictadigital.io</b> under eight different sender names &mdash; Brook himself,
&ldquo;Desk of Brook Hiddink&rdquo;, Anastasia on his team, a fake Romanian tech-support
guy, and a final-notice alias. Click any row to read it exactly as it landed.</p>
<div class="tiles">
<div class="tile"><b>{len(rows)}</b><span>emails captured</span></div>
<div class="tile"><b>8</b><span>sender identities</span></div>
<div class="tile"><b>{len(golden)}</b><span>golden-ticket emails</span></div>
<div class="tile"><b>47</b><span>days of sequence</span></div>
<div class="tile"><b>1</b><span>sending domain</span></div>
</div>
<div class="bar">
<input id="q" placeholder="Search subject, sender or body text&hellip;">
<button class="btn ghost" id="fgold">Golden ticket only</button>
<a class="btn" href="brook-hiddink-emails.zip" download>Download all (PNG + HTML)</a>
</div></div>

<div class="split">
<div class="inbox" id="inbox">{"".join(items)}</div>
<div class="reader" id="reader"><div class="empty">Pick an email on the left.</div></div>
</div></div>

<script>
const R = {data};
const byN = Object.fromEntries(R.map(r=>[r.n,r]));
let mode = 'shot';
const reader = document.getElementById('reader');
const inbox  = document.getElementById('inbox');

function esc(s){{return (s||'').replace(/[&<>]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;'}})[c]);}}

function render(n,scroll){{
  const r = byN[n]; if(!r) return;
  document.querySelectorAll('.row').forEach(el=>el.classList.toggle('on',+el.dataset.i===n));
  if(scroll){{
    const row=document.querySelector('.row.on');
    if(row) inbox.scrollTop = row.offsetTop - inbox.clientHeight/3;
  }}
  reader.innerHTML =
    '<div class="rhead"><h2>'+esc(r.subject)+(r.golden?' <span class=gt>golden ticket</span>':'')+'</h2>'+
    '<div class="who"><b>'+esc(r.from)+'</b> &lt;'+esc(r.email)+'&gt;</div>'+
    '<div class="stamp">'+esc(r.date)+' '+esc(r.time)+' CST &middot; email #'+r.n+
    (r.since?' &middot; '+esc(r.since)+' after opt-in':'')+'</div></div>'+
    '<div class="rtools">'+
      '<button class="btn ghost'+(mode==='shot'?' on':'')+'" data-m="shot">Screenshot</button>'+
      '<button class="btn ghost'+(mode==='text'?' on':'')+'" data-m="text">Plain text</button>'+
      (r.has_html?'<a class="btn ghost" target="_blank" href="media/emails/'+r.slug+'.html">Open original HTML &nearr;</a>':'')+
      '<a class="btn ghost" download href="media/emails/'+r.slug+'.png">Save PNG</a>'+
    '</div>'+
    (mode==='shot'
      ? '<div class="rbody"><img src="media/emails/'+r.slug+'.png" alt=""></div>'
      : '<div class="plain">'+esc(r.body)+'</div>');
  reader.querySelectorAll('[data-m]').forEach(b=>b.onclick=()=>{{mode=b.dataset.m;render(n);}});
  history.replaceState(null,'','#e'+n);
}}

inbox.addEventListener('click',e=>{{
  const row = e.target.closest('.row'); if(row) render(+row.dataset.i);
}});

let goldOnly=false;
function filter(){{
  const q=document.getElementById('q').value.toLowerCase();
  document.querySelectorAll('.row').forEach(el=>{{
    const r=byN[+el.dataset.i];
    const hit=!q||(r.subject+' '+r.from+' '+r.body).toLowerCase().includes(q);
    el.classList.toggle('hide',!(hit&&(!goldOnly||r.golden)));
  }});
}}
document.getElementById('q').addEventListener('input',filter);
document.getElementById('fgold').onclick=function(){{
  goldOnly=!goldOnly; this.classList.toggle('on',goldOnly); filter();
}};

const start = +(location.hash.match(/#e(\\d+)/)||[])[1] || {golden[0] if golden else 1};
render(start,true);
</script>
</body></html>"""

open(os.path.join(HERE, "emails.html"), "w", encoding="utf-8").write(html)

# wire Emails into the nav on every other page
for page in ("index.html", "vsl.html", "webinar.html", "sms.html",
             "transcripts.html", "ads.html"):
    p = os.path.join(HERE, page)
    if not os.path.exists(p):
        continue
    s = open(p, encoding="utf-8").read()
    if 'href="emails.html"' in s:
        continue
    s = s.replace('<a href="sms.html">SMS</a>',
                  '<a href="emails.html">Emails</a><a href="sms.html">SMS</a>')
    s = s.replace("<a href=\"sms.html\" class='on'>SMS</a>",
                  "<a href=\"emails.html\">Emails</a><a href=\"sms.html\" class='on'>SMS</a>")
    open(p, "w", encoding="utf-8").write(s)

print(f"emails.html  {len(rows)} emails, {len(golden)} golden-ticket "
      f"(#{', #'.join(str(g) for g in golden)})")
print(f"zip          {os.path.getsize(zip_path)/1048576:.0f} MB")

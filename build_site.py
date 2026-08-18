#!/usr/bin/env python3
"""Build the Shelby Sapp swipe site.

Generates a hub plus one page per asset class from the captured data in data/
and the optimised images in media/. Everything is static; images are real files
rather than base64 so the pages stay light with ~250 frames in play.

Run: python3 build_site.py
"""
import json, os, re, html

ROOT = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(ROOT, "data")
M = os.path.join(ROOT, "media")

SITE = "Brook Hiddink / High Ticket — Swipe"
CAPTURED = "30 July 2026"

VSL_DECK = "https://docs.google.com/presentation/d/1hBEsazAMhJMSDQbtydOS6YfiM9li39e8ad62mkA_ikA/edit"
WEB_DECK = "https://docs.google.com/presentation/d/1p7BuTpqLaZK2sz0BvXNaEUyRqbBEgqewUnVCoegkAaM/edit"

PAGES = [
    ("index.html", "Overview"),
    ("vsl.html", "The VSL"),
    ("webinar.html", "Webinar"),
    ("sms.html", "SMS"),
    ("transcripts.html", "Transcripts"),
    ("ads.html", "Ads"),
    ("board.html", "Wired board"),
]

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{--ink:#0f172a;--muted:#64748b;--line:#e2e8f0;--panel:#f8fafc;--bg:#eef0f3;
 --accent:#4f46e5;--ever:#059669;--event:#ea580c;--rose:#9f1239}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--ink);
 font-family:Inter,system-ui,-apple-system,'Segoe UI',sans-serif;
 -webkit-font-smoothing:antialiased;line-height:1.55}
h1,h2,h3,h4{font-weight:500;letter-spacing:-.02em}
a{color:inherit}
.wrap{max-width:1180px;margin:0 auto;padding:0 28px}
header.top{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:50}
.topin{max-width:1180px;margin:0 auto;padding:0 28px;display:flex;align-items:center;
 gap:26px;height:60px}
.brand{font-size:15px;font-weight:500;white-space:nowrap}
.brand span{color:var(--muted);font-weight:400}
nav.main{display:flex;gap:20px;overflow-x:auto;scrollbar-width:none}
nav.main::-webkit-scrollbar{display:none}
nav.main a{font-size:14px;color:var(--muted);text-decoration:none;white-space:nowrap;
 padding:6px 0;border-bottom:2px solid transparent}
nav.main a:hover{color:var(--ink)}
nav.main a.on{color:var(--ink);border-bottom-color:var(--accent)}
.hero{padding:54px 0 30px}
.kick{font-size:13px;letter-spacing:.11em;text-transform:uppercase;color:var(--muted);
 margin-bottom:12px}
.hero h1{font-size:44px;margin-bottom:14px}
.hero p{font-size:18px;color:#475569;max-width:820px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(178px,1fr));gap:14px;
 margin:30px 0 8px}
.tile{background:#fff;border:1px solid var(--line);border-radius:12px;padding:17px 19px}
.tile b{display:block;font-size:26px;font-weight:500;letter-spacing:-.03em}
.tile span{font-size:12.5px;color:var(--muted);display:block;margin-top:3px;line-height:1.4}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(268px,1fr));gap:16px;
 margin:26px 0 50px}
a.card{background:#fff;border:1px solid var(--line);border-radius:14px;padding:22px;
 text-decoration:none;display:block;transition:.15s;border-top:4px solid var(--accent)}
a.card:hover{transform:translateY(-3px);box-shadow:0 12px 28px rgba(15,23,42,.13);
 border-color:#94a3b8}
a.card h3{font-size:19px;margin-bottom:7px}
a.card p{font-size:14px;color:#475569;line-height:1.55}
a.card em{font-style:normal;font-size:12px;color:var(--muted);display:block;margin-top:11px;
 font-family:ui-monospace,Menlo,monospace}
section{padding:34px 0}
section h2{font-size:29px;margin-bottom:9px}
section .lede{font-size:16.5px;color:#475569;max-width:840px;margin-bottom:22px}
.panel{background:#fff;border:1px solid var(--line);border-radius:14px;padding:26px;
 margin-bottom:18px}
.panel h3{font-size:20px;margin-bottom:10px}
.panel p{font-size:15px;color:#334155;margin-bottom:11px}
.panel p:last-child{margin-bottom:0}
.panel ul{margin:0 0 12px 19px}
.panel li{font-size:15px;color:#334155;margin-bottom:7px}
blockquote{border-left:3px solid var(--accent);padding:3px 0 3px 16px;margin:14px 0;
 font-size:15px;color:#1e293b;background:#f8fafc}
blockquote em{font-style:normal;color:var(--muted);font-size:13px;display:block;margin-top:5px}
table{width:100%;border-collapse:collapse;font-size:14.5px;margin:6px 0 14px}
th,td{text-align:left;padding:9px 11px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-weight:500;color:var(--muted);font-size:12.5px;letter-spacing:.06em;
 text-transform:uppercase}
.scroller{overflow-x:auto}
.grid{display:grid;gap:13px}
.g6{grid-template-columns:repeat(auto-fill,minmax(178px,1fr))}
.g4{grid-template-columns:repeat(auto-fill,minmax(232px,1fr))}
figure.sh{background:#fff;border:1px solid var(--line);border-radius:10px;overflow:hidden;
 cursor:zoom-in;transition:.13s}
figure.sh:hover{border-color:#94a3b8;box-shadow:0 8px 20px rgba(15,23,42,.13)}
figure.sh img{display:block;width:100%;height:auto;background:var(--panel)}
figure.sh figcaption{padding:8px 10px;font-size:11.5px;color:var(--muted);
 font-family:ui-monospace,Menlo,monospace;display:flex;justify-content:space-between;gap:8px}
figure.sh figcaption b{color:var(--ink);font-weight:500}
.anchor figcaption b{color:#b45309}
.mailcap{padding:9px 11px}
.mailcap b{display:block;font-size:11px;color:var(--muted);font-weight:400;
 font-family:ui-monospace,Menlo,monospace;margin-bottom:3px}
.mailcap span{font-size:12.5px;line-height:1.35;display:block}
.tx{background:#fff;border:1px solid var(--line);border-radius:14px;padding:30px 34px;
 max-height:640px;overflow-y:auto}
.tx p{font-size:15.5px;color:#1e293b;margin-bottom:15px;line-height:1.72;max-width:74ch}
.tx p b{font-family:ui-monospace,Menlo,monospace;font-size:12.5px;color:var(--accent);
 font-weight:500;margin-right:7px}
.bar{display:flex;gap:9px;flex-wrap:wrap;margin-bottom:16px}
.bar button,.bar a.btn{font:inherit;font-size:13.5px;padding:8px 15px;border-radius:8px;
 border:1px solid var(--line);background:#fff;cursor:pointer;text-decoration:none;color:inherit}
.bar button:hover,.bar a.btn:hover{border-color:#94a3b8}
.bar button.on{background:var(--ink);color:#fff;border-color:var(--ink)}
.pill{display:inline-block;font-size:11px;letter-spacing:.08em;text-transform:uppercase;
 padding:3px 9px;border-radius:5px;background:#eef2ff;color:#4338ca;margin:0 5px 5px 0}
.pill.g{background:#ecfdf5;color:#047857}
.pill.o{background:#fff7ed;color:#c2410c}
.note{border:1px solid #fde68a;background:#fffbeb;border-radius:10px;padding:15px 18px;
 font-size:14px;color:#78350f;margin-bottom:18px}
footer{border-top:1px solid var(--line);margin-top:40px;padding:26px 0 50px;
 font-size:13px;color:var(--muted)}
#lb{position:fixed;inset:0;background:rgba(8,12,22,.93);display:none;z-index:200;
 align-items:center;justify-content:center;flex-direction:column;gap:14px;padding:26px}
#lb.on{display:flex}
#lb img{max-width:96vw;max-height:83vh;object-fit:contain;border-radius:5px}
#lb .meta{color:#cbd5e1;font-size:13px;font-family:ui-monospace,Menlo,monospace;
 display:flex;gap:18px;align-items:center}
#lb .meta a{color:#93c5fd}
#lb .x{position:absolute;top:16px;right:22px;color:#94a3b8;font-size:30px;cursor:pointer;
 line-height:1}
@media(max-width:720px){.hero h1{font-size:33px}.wrap,.topin{padding:0 17px}
 .tx{padding:20px}}
"""

LB = """
<div id="lb"><span class="x" onclick="closeLb()">&times;</span>
<img id="lbi" alt=""><div class="meta"><span id="lbm"></span></div></div>
<script>
function openLb(i){LBI=i;var s=LBS[i];if(!s)return;
 document.getElementById('lbi').src=s.full;
 document.getElementById('lbm').textContent=s.cap;
 document.getElementById('lb').classList.add('on');}
function closeLb(){document.getElementById('lb').classList.remove('on');}
document.addEventListener('keydown',function(e){
 var o=document.getElementById('lb').classList.contains('on');if(!o)return;
 if(e.key==='Escape')closeLb();
 if(e.key==='ArrowRight'&&LBI<LBS.length-1)openLb(LBI+1);
 if(e.key==='ArrowLeft'&&LBI>0)openLb(LBI-1);});
document.getElementById('lb').addEventListener('click',function(e){
 if(e.target.id==='lb')closeLb();});
</script>
"""


def shell(active, title, body, extra_head=""):
    pages = [x for x in PAGES
             if os.path.exists(os.path.join(ROOT, x[0])) or x[0] == active]
    nav = "".join(
        f'<a href="{h}"{" class=\'on\'" if h == active else ""}>{html.escape(t)}</a>'
        for h, t in pages)
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><style>{CSS}</style>
<script>var LBS=[],LBI=0;</script>{extra_head}</head><body>
<header class="top"><div class="topin">
<div class="brand">Brook Hiddink <span>/ High Ticket</span></div>
<nav class="main">{nav}</nav></div></header>
{body}
<footer><div class="wrap">Private research swipe. Captured {CAPTURED}.
Screenshots are unaltered frames from the source recordings and live pages —
branding and copyright notices preserved. Not affiliated with High Ticket / Brook Hiddink.
</div></footer>{LB}</body></html>"""


def load(name):
    with open(os.path.join(D, name)) as fh:
        return json.load(fh)


def gallery(items, cls="g6", offset=0):
    """items: dicts with thumb/full/cap/sub. offset keeps lightbox indices
    correct when a page renders more than one gallery."""
    figs = []
    for i, it in enumerate(items):
        extra = " anchor" if it.get("anchor") else ""
        figs.append(
            f'<figure class="sh{extra}" onclick="openLb({offset + i})">'
            f'<img loading="lazy" src="{it["thumb"]}" alt="{html.escape(it["cap"])}">'
            f'<figcaption><b>{html.escape(it["cap"])}</b>'
            f'<span>{html.escape(it.get("sub",""))}</span></figcaption></figure>')
    data = json.dumps([{"full": it["full"],
                        "cap": it["cap"] + ("  ·  " + it["sub"] if it.get("sub") else "")}
                       for it in items])
    return (f'<div class="grid {cls}">' + "".join(figs) + "</div>"
            f'<script>LBS=LBS.concat({data});</script>')


# ----------------------------------------------------------------- data prep

# ----------------------------------------------------------------- pages

# ----------------------------------------------------------------- segments
# Figures below come from the Copy Bank doc (3,217 ad records analysed).

COPY_BANK = ("https://docs.google.com/document/d/"
             "1OHvjtoCEjnUjHU-STlUTb2t-xX94E7tNuq4rLp7PVw0/edit")

ADS_DEST = [
    ("Masterclass opt-in (primary)", 1752, 1283, 213),
    ("Learn opt-in (newer page)", 472, 215, 57),
    ("Next-day urgency opt-in", 146, 131, 21),
    ("Legacy webinar reg (Apr 25)", 279, 279, 1),
    ("Free-webinar-opp", 185, 180, 2),
    ("Women and Wealth Conference", 76, 48, 1),
    ("Facebook / Instagram profile", 44, 44, 13),
    ("Other, now sunset", 169, 167, 0),
]
ADS_AVATAR = [
    ("Existing salesperson (poach)", 1551, 167),
    ("Server, retail, hourly", 1287, 193),
    ("Student, grad school", 1113, 147),
    ("9-5 / corporate", 1089, 120),
    ("20s, status-seeking", 510, 62),
    ("Teacher, educator", 441, 63),
    ("Mom, stay-at-home", 389, 73),
    ("Nurse, healthcare", 384, 62),
    ("Laid off, job loss", 92, 30),
]
ADS_CONTENT = [
    ("Direct invite, event push", 1795, 209),
    ("Founder story, origin", 1086, 143),
    ("Testimonial, student result", 1039, 137),
    ("Mechanism, how it works", 494, 81),
    ("Objection, reframe", 471, 58),
]
ADS_FORMAT = [("Video", 2059), ("DCO", 759), ("Image", 384), ("Carousel", 15)]
ADS_CONTROLS = [
    (304, "Masterclass", "general", "image / DCO, no script"),
    (274, "Masterclass", "Existing salesperson",
     "you're not bad at sales, you're just in a bad sales job"),
    (267, "Masterclass", "Teacher, 9-5",
     "the most powerful thing a woman can do is become financially…"),
    (254, "Learn", "Server, hourly",
     "I just got off a call and somebody asked me how do…"),
    (177, "Learn", "9-5, Existing sales",
     "all the bad bitches driving G-Wagons, living in penthouses…"),
    (177, "Masterclass", "Nurse, Teacher",
     "this one's for the nurse working back-to-back shifts"),
    (177, "Learn", "Mom, 9-5", "so I just had a video go mega viral because one of…"),
    (177, "Learn", "Server, Existing sales",
     "last summer I made $300,000 selling door to door…"),
    (177, "Next-day", "20s, status", "put a finger down if all you want to do is…"),
]

VSL_VARIANTS = [
    ("Confirmation page VSL", "0:01:31", "~230",
     "masterclass.shesellsremote.com/thank-you", "GoHighLevel",
     "Plays the second they register. Two jobs only: check your email for the Zoom "
     "link, and block 90 minutes in your calendar. Pre-frames active participation."),
    ("Short cut VSL", "0:17:02", "3,344",
     "shortvideo.shesellsremote.com/10-min-video", "Vimeo 1092420877",
     "The evergreen VSL for people who will not sit through the webinar. "
     "Talking head, name/email/phone gate in front of it."),
    ("Post-booking VSL", "0:18:39", "3,926",
     "training.shesellsremote.com/ty", "Vidalytics",
     "Plays after a call is booked. Explains the program and pre-handles six "
     "objections before the closer ever dials. Ranked the #1 thing to steal."),
    ("access3 backend VSL", "0:21:31", "4,876",
     "training.shesellsremote.com/access3", "Vidalytics fZOZ_kMmSW5DjvF9",
     "Email-traffic-only retargeting VSL. Opens on the founder-can't-take-the-calls "
     "story rather than her own origin. Tagged EB-VSL-Weds-29th-July."),
    ("Long cut / webinar", "2:41:18", "29,931",
     "video.shesellsremote.com/10-min-video", "Wistia fc62di18zn",
     "The full presented deck, 177 slides. Sold as a VSL link but it is the "
     "masterclass recording."),
]

EMAIL_PHASE_1 = [
    ("Confirm your spot? (action required)", "registration receipt"),
    ("No time for this masterclass? That's why you NEED it…", "objection: no time"),
    ("B.S. radar going off?", "objection: scepticism"),
    ("Tired of all talk, no results? (I feel you)", "objection: been burned"),
    ("No sales experience? Perfect.", "objection: no experience"),
    ("“What will people think of me?”", "objection: social judgment"),
    ("It's TODAY, hot girl", "day-of · morning"),
    ("You didn't forget about tonight… right?", "day-of · 5pm"),
    ("This is your one-hour warning, bestie", "day-of · T-60"),
]


def tbl(headers, rows, widths=None):
    th = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
    tr = "".join("<tr>" + "".join(
        f"<td>{html.escape(str(c)) if not isinstance(c,str) or not c.startswith('<') else c}</td>"
        for c in r) + "</tr>" for r in rows)
    return (f'<div class="panel scroller"><table><thead><tr>{th}</tr></thead>'
            f"<tbody>{tr}</tbody></table></div>")




def media_map(prefix):
    with open(os.path.join(M, f"{prefix}media.json")) as fh:
        return {m["stem"]: m for m in json.load(fh)}


BROOK_OBJ = [
    ("1", "I've Never Sold a Product Online Before", "0:48"),
    ("6", "Can I Do This With a Full Time Job", "0:26"),
    ("8", "I'm Not Tech Savvy. What Skills Are Required", "0:26"),
    ("15", "Do You Have a Guarantee", "1:04"),
    ("18", "How Many Hours Per Day Does This Require", "0:23"),
    ("21", "What's The Timeframe For Your First Sale", "0:21"),
    ("25", "How Long Have You Been Doing It. Prove It", "0:35"),
    ("26", "What Are Realistic Income/Results Expectations", "0:36"),
]

BROOK_SMS = [
    ("Brook Hiddink", "(720) 610-3324",
     "\"hey is this Hans? it's brook hiddink\" then \"think you were just watching one "
     "of my ads and signed up for my workshop later - can you confirm you'll be "
     "attending?\" then \"quick q before tonight - what made you sign up? want make "
     "sure i actually cover the thing you care about\""),
    ("Anastasia, \"Brook's personal assistant\"", "(877) 730-9884",
     "Confirms the seat, sends the room link at go-live, chases the no-show next morning."),
    ("Jack, \"from High Ticket with Brook Hiddink\"", "(814) 822-5129",
     "Post-event: \"Did you make it to our Webinar? Here is the recording if you missed it.\""),
]


def page_index():
    vids = load("brook_videos.json")
    mm = media_map("brook_")
    shots = [{"thumb": "media/" + m["thumb"], "full": "media/" + m["full"],
              "cap": k.split("_", 1)[1].replace("_", " "),
              "sub": "VSL funnel" if k.startswith("VSL") else "Webinar funnel"}
             for k, m in sorted(mm.items())]
    long_v = [v for v in vids if v["secs"] > 900]
    short_v = [v for v in vids if v["secs"] <= 900]
    total = sum(v["secs"] for v in vids)
    vt = tbl(["Runtime", "Video", "Size"],
             [(v["hhmmss"], v["title"], f'{v["size_mb"]} MB') for v in vids])
    ot = tbl(["#", "Objection it kills", "Runtime"], BROOK_OBJ)
    st = tbl(["Persona", "Number", "What they send"], BROOK_SMS)
    tiles = [(f"{len(vids)}", "videos captured"),
             (f"{total//3600}h {total%3600//60:02d}m", "of video"),
             ("585", "ads analysed"),
             ("11", "objection videos"),
             ("3", "SMS personas"),
             ("2", "live funnels")]
    tl = "".join(f'<div class="tile"><b>{a}</b><span>{b}</span></div>' for a, b in tiles)

    body = f"""<div class="wrap">
<div class="hero"><div class="kick">Funnel swipe · captured {CAPTURED}</div>
<h1>Brook Hiddink — High Ticket</h1>
<p>Law-student-to-$30M e-commerce coach. <b>Two funnels at two completely different
price points, and they do not feed each other.</b> A 42-minute VSL into a high-ticket
application and a booked call. And a nightly live event that sells a <b>$995 product on
a direct checkout</b> — no call, no application. Everything here is evidence pulled off
his live funnel.</p>
<div class="tiles">{tl}</div>
<div class="bar" style="margin-top:24px"><a class="btn" href="ads.html">
His ads, segmented &rarr;</a></div></div>

<section><h2>The two things worth stealing</h2>
<div class="panel">
<h3>1. A numbered objection library, played before the call</h3>
<p>Eleven short videos, 20 seconds to 3 minutes, served on the pre-call page. Titled by
objection number, and the numbering runs to at least 26 — so this is a fraction of what
exists.</p>{ot}
<p>Most competitors do this job with one long post-booking video. Brook has broken it
into a library and can serve exactly the objection a given lead is likely to have.
<b>This is the single most copyable asset in the funnel.</b></p>
</div>
<div class="panel">
<h3>2. Three SMS personas, before the event</h3>
<p>Every text arrives from a different named human, via Google Voice numbers.</p>{st}
<p>He opens with a personal "hey is this you?", follows with an assistant handling
logistics, and closes with a third name pushing the replay. The first message asks a
real question — <em>"what made you sign up? want make sure i actually cover the thing
you care about"</em> — which is reply-bait, not a reminder.</p>
</div></section>

<section><h2>The video library</h2>
<p class="lede">{len(long_v)} long-form case studies ({sum(v["secs"] for v in long_v)//60} min)
and {len(short_v)} short objection and utility clips, all at source quality.</p>{vt}</section>

<section><h2>Funnel pages</h2>
<p class="lede">Both funnels captured end to end, including the forced-consumption step
most people never see.</p>{gallery(shots, "g4", 0)}</section>

<section><h2>How his funnel runs</h2>
<div class="panel"><ul>
<li><b>VSL path.</b> <code>highticket.io/freetraining</code> serves a 42:46 VSL on a
player that hides its file, then an application, a scheduling page, and a confirmation
page stacked with case-study interviews.</li>
<li><b>Webinar path — a different business.</b> A VIP opt-in, a bridge page selling a
paid VIP upgrade before the event has even happened, a countdown thank-you page, then a
live Zoom room. The pitch closes to a <b>$995 direct checkout</b> at
<code>1orderaway.com/now</code>, capped at <b>97 spots</b>, with six bonuses stacked to
a claimed $100k+, a money-back guarantee and a <b>$500 cash rebate</b> when you post
your first sale over $1,000.</li>
<li><b>The two funnels connect only at the DQ.</b> Fail the high-ticket application and
you are routed into the $995 webinar offer. A downsell by design.</li>
<li><b>No-shows are auto-registered into an encore</b> about 2.5 hours after the live
room ends. Verified across two separate cycles.</li>
<li><b>The bridge-page upsell is the notable move</b> — he monetises between
registration and attendance.</li>
</ul></div></section>
</div>"""
    return shell("index.html", SITE, body)


def page_ads():
    a = load("brook_ads.json")
    pages = tbl(["Facebook page", "Ads", "Still live", "Survival"],
                [(p["k"], p["tot"], p["live"], f'{p["pct"]}%') for p in a["pages"]])
    fmts = tbl(["Format", "Ads", "Still live", "Survival"],
               [(f["k"], f["tot"], f["live"], f'{f["pct"]}%') for f in a["formats"]])
    wins = "".join(f"<li>{html.escape(w)}</li>" for w in a["wins"])
    dead = "".join(f"<li>{html.escape(w)}</li>" for w in a["dead"])
    body = f"""<div class="wrap">
<div class="hero"><div class="kick">Segment · paid traffic</div>
<h1>His ads, segmented</h1>
<p>{a['total']} ads pulled from the Meta Ad Library, {a['live']} still live. The recent
cohort — launched April 2026 onward — is {a['cohort_n']} ads with {a['cohort_live']}
live, and that is the set worth reading.</p></div>

<section><h2>He runs five pages. Only the plain one works.</h2>{pages}
<div class="panel"><p>Each page is a different credibility framing, and the result is
blunt: <b>every credential-stacked page is dead.</b> "HighTicket.io CEO" and "Law School
to 8 Figures E-Commerce Entrepreneur" have zero live ads between them. The page that
just says <b>Brook Hiddink</b> carries 347 ads at 39% survival.</p>
<p>He tested whether stacking authority in the advertiser name helps. It does not.</p>
</div></section>

<section><h2>What he still runs vs what he killed</h2>
<div class="panel">
<h3>Live — his current winners</h3><ul>{wins}</ul>
<h3>Killed</h3><ul>{dead}</ul>
<p><b>His testimonial ads and his origin story are dead.</b> Trustpilot proof, "Real
Wins from Real People", "#1 High-Ticket eCommerce Program on the Planet", "Mom, I'm
dropping out of law school" — all killed.</p>
<p>What survives is event urgency and conversational pattern-interrupts that read like a
text message rather than an ad: <em>"This is getting a little silly"</em>,
<em>"One sauna"</em>, <em>"I owe an apology to anyone who scrolled past one of our ads
thinking 'another guru pitch'"</em>, <em>"At 62, you assumed this train had already left
the station"</em>.</p></div></section>

<section><h2>By format</h2>{fmts}
<div class="panel"><p>Video at 35% survival against carousel at 4%. Static creative is
not a real lane for him.</p></div></section>

<div class="note"><b>Sample note.</b> 600 ads pulled newest-first, not his entire
history — the Ad Library pull is metered. A recent cohort, directionally solid, but do
not read the totals as his lifetime ad count.</div>
</div>"""
    return shell("ads.html", "Ads — " + SITE, body)


def main():
    out = {"index.html": page_index(), "vsl.html": page_vsl(),
           "sms.html": page_sms(), "transcripts.html": page_transcripts(),
           "ads.html": page_ads()}
    # The webinar page only builds once its frames have been extracted.
    if os.path.exists(os.path.join(D, "webinar_frames.json")):
        out["webinar.html"] = page_webinar()
    else:
        print("  webinar.html   skipped (frames still extracting)")
    for name, txt in out.items():
        with open(os.path.join(ROOT, name), "w") as fh:
            fh.write(txt)
        print(f"  {name:14s} {len(txt)/1024:7.1f} KB")
    print(f"built {len(out)} pages")




def page_vsl():
    idx = load("vsl_frames.json")
    mm = media_map("vsl_")
    items = []
    for sl in idx["slides"]:
        stem = os.path.splitext(sl["file"])[0]
        m = mm.get(stem)
        if not m:
            continue
        items.append({"thumb": "media/" + m["thumb"], "full": "media/" + m["full"],
                      "cap": f'{sl["n"]:03d}', "sub": sl["timestamp"],
                      "anchor": sl.get("type") == "anchor"})
    body = f"""<div class="wrap">
<div class="hero"><div class="kick">Asset · main VSL</div>
<h1>The 42-minute VSL</h1>
<p><code>highticket.io/freetraining</code> · 42:46 · served on a converteai/vturb player
that hides its file from the page source. {len(items)} distinct visual states captured,
roughly one every three seconds.</p></div>

<section><h2>Why the cut rate matters</h2>
<div class="panel">
<p>Shelby's 17-minute VSL produced 64 visual changes. Brook's 42-minute VSL produced
<b>{len(items)}</b>. Per minute that is more than four times the cutting.</p>
<p>He is not talking to camera for long stretches. Every few seconds it moves to
b-roll, a software demo, a review screenshot, a text card or a different framing. The
captions are burned in and animated. <b>The edit is doing as much work as the
script.</b></p>
</div></section>

<section><h2>Every visual state</h2>
<p class="lede">Captions are the frame number and its timestamp. Click any frame to open
it full size; arrow keys move through.</p>{gallery(items, "g6", 0)}</section>
</div>"""
    return shell("vsl.html", "The VSL — " + SITE, body)


def page_sms():
    d = load("brook_sms.json")
    rows = []
    for p in d["personas"]:
        msgs = "<span>" + "<br>".join(
            f"&ldquo;{html.escape(m)}&rdquo;" for m in p["messages"]) + "</span>"
        rows.append((p["name"], p["number"], p["role"], msgs))
    t = tbl(["Persona", "Number", "Role", "What they send"], rows)
    ladder = "".join(f"<li>&ldquo;{html.escape(m)}&rdquo;</li>" for m in d["downsell_ladder"])
    angles = "".join(f"<li>&ldquo;{html.escape(m)}&rdquo;</li>" for m in d["angle_tests"])
    body = f"""<div class="wrap">
<div class="hero"><div class="kick">Asset · SMS</div>
<h1>Three people who are all the same bot</h1>
<p>Every text arrives from a different named human on its own Google Voice number.
Two full registration cycles captured, a month apart.</p></div>

<section><h2>The personas</h2>{t}</section>

<section><h2>The tell: it is the same script every cycle</h2>
<div class="panel">
<p>Registering in June and again in July produced the <b>identical four-message
sequence</b> from "Brook", word for word, only the name changed:</p>
<blockquote>"hey is this Will? it's brook from high ticket" &rarr; "saw you grabbed a
seat on my workshop later. you excited?" &rarr; "you planning on joining from your cell
or laptop?" &rarr; "quick q before tonight - what made you sign up?"
<em>21 June 2026</em></blockquote>
<blockquote>"hey is this Hans? it's brook hiddink" &rarr; "think you were just watching
one of my ads and signed up for my workshop later - can you confirm you'll be
attending?" &rarr; "you planning on joining from your cell or laptop?" &rarr; "quick q
before tonight - what made you sign up?"<em>21 July 2026</em></blockquote>
<p>It reads personal and it is fully automated. <b>The move worth stealing is the
fourth message</b> — asking what made them sign up. It is reply-bait dressed as
service, and a reply is what keeps the thread deliverable.</p>
</div></section>

<section><h2>The downsell ladder runs over SMS too</h2>
<div class="panel"><p>When the main program does not land, the same channel walks the
lead down to a cheaper offer and then to payments.</p><ul>{ladder}</ul>
<p>Main program &rarr; <b>High Ticket Accelerator Lite</b> &rarr; <b>$295/month</b>.
All of it by text, with a hard midnight deadline.</p></div></section>

<section><h2>He tests completely different avatars by SMS</h2>
<div class="panel"><ul>{angles}</ul>
<p>Retirees short $2,000 a month, parents missing their kids growing up, 9-5ers who
dread Monday. Same offer, different pain, delivered to the same list.</p></div></section>

<div class="note"><b>The contrast with Shelby.</b> She sends nothing by text between
registration and her class — her pre-class channel is email only, 43 days straight.
Brook barely emails and texts constantly as three people. They are near-exact
inverses.</div>
</div>"""
    return shell("sms.html", "SMS — " + SITE, body)



def page_transcripts():
    ts = load("brook_transcripts.json")
    total = sum(t["words"] for t in ts)
    nav = "".join(
        f'<a class="btn" href="#t{i}">{html.escape(t["title"][:34])}</a>'
        for i, t in enumerate(ts))
    blocks = []
    for i, t in enumerate(ts):
        paras = "".join(f'<p><b>{p["t"]}</b>{html.escape(p["x"])}</p>' for p in t["paras"])
        blocks.append(
            f'<section id="t{i}"><h2>{html.escape(t["title"])}</h2>'
            f'<p class="lede">{t["minutes"]} min · {t["words"]:,} words</p>'
            f'<div class="tx">{paras}</div></section>')
    body = f"""<div class="wrap">
<div class="hero"><div class="kick">Asset · transcripts</div>
<h1>Every video, transcribed</h1>
<p>{len(ts)} videos · <b>{total:,} words</b>. Machine transcription
(whisper.cpp <code>small.en</code>), timestamped, not proofread.</p>
<div class="bar" style="margin-top:18px">{nav}</div></div>
{''.join(blocks)}
</div>"""
    return shell("transcripts.html", "Transcripts — " + SITE, body)



def page_webinar():
    idx = load("webinar_frames.json")
    mm = media_map("web_")
    items = []
    for sl in idx["slides"]:
        stem = os.path.splitext(sl["file"])[0]
        m = mm.get(stem)
        if not m:
            continue
        items.append({"thumb": "media/" + m["thumb"], "full": "media/" + m["full"],
                      "cap": f'{sl["n"]:03d}', "sub": sl["timestamp"],
                      "anchor": sl.get("type") == "anchor"})
    tr = load("brook_transcripts.json")
    wt = next((t for t in tr if "WEBINAR" in t["title"].upper()), None)
    paras = ""
    if wt:
        paras = "".join(f'<p><b>{p["t"]}</b>{html.escape(p["x"])}</p>' for p in wt["paras"])
    body = f"""<div class="wrap">
<div class="hero"><div class="kick">Asset · live webinar</div>
<h1>"One Order Away Method"</h1>
<p>The full live event, 2h 14m, recovered from the replay room. Titled
<em>"How Law Student Used A.I. To Build a $5M Business in 18 Months…"</em>, run on
WebinarJam rather than as a hosted file.</p>
<div class="bar"><a class="btn" href="#transcript">Jump to transcript</a></div></div>

<section><h2>How it was recovered</h2>
<div class="panel">
<p>There is no video file on his pages. The webinar runs live on WebinarJam and the
replay sits behind an entry gate asking for name, email and a country/state
declaration. Past that gate the room streams a signed Vimeo MP4, which is what is
captured here.</p>
<p><b>Worth noting for our own funnel:</b> the replay link he texts out is
single-use-looking but actually re-entrant — the same token regenerates a fresh room
session. His scarcity language around the replay ("Closing This Tab Ends The Session")
is not enforced.</p>
</div></section>

<section><h2>Every slide and visual state</h2>
<p class="lede">{len(items)} states captured across the 2h 14m. Amber numbers are
timeline anchors, not detected changes.</p>{gallery(items, "g6", 0)}</section>

<section id="transcript"><h2>Full transcript</h2>
<p class="lede">{(f"{len(wt['paras'])} timestamped paragraphs · {wt['words']:,} words."
   if wt else "Transcript pending.")}</p>
<div class="tx">{paras}</div></section>
</div>"""
    return shell("webinar.html", "Webinar — " + SITE, body)

if __name__ == "__main__":
    main()

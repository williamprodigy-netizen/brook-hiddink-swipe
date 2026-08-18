#!/usr/bin/env python3
"""Brook Hiddink — whole-business wired board.

One pannable canvas. Every funnel step is the real screenshot, wired together.
Two mechanisms run side by side: a 42-minute VSL into an application, and a
nightly WebinarJam event with a paid VIP upsell sitting between registration
and attendance. The SMS layer runs across both.

Layout rule: one column per funnel STEP, parallel variants stack vertically
inside that column so an arrow never crosses a card it is not pointing at.

Run:  python3 build_board.py   ->  board.html
"""
import base64, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
DIMS = json.load(open(os.path.join(HERE, "dims.json")))
SHOTS_SRC = os.path.join(HERE, "media", "full")

CARD_W = 330
CHROME = 166
X = {1: 60, 2: 470, 3: 880, 4: 1290, 5: 1700, 6: 2110, 7: 2520}

# id -> (asset, col, y, lane, title, url, note)
SHOTS = {
    "vsl_app": ("VSL_01_VSL_application", 2, 150, "paid", "VSL + application",
                "https://www.highticket.io/freetraining",
                "42:46 VSL on a converteai/vturb player that hides its file. "
                "Application sits under it."),
    "sched": ("VSL_02_Schedule", 3, 150, "paid", "Schedule a call",
              "https://www.highticket.io/schedule-a",
              "Straight to booking. No price shown anywhere before this point."),
    "confirm": ("VSL_03_Confirmation_page", 4, 150, "paid", "Confirmation",
                "https://www.highticket.io/thank-you-a",
                "Stacked with 11 case-study interviews, 16 to 31 minutes each. "
                "4h 25m of proof on one page."),
    "precall": ("VSL_04_Pre-call_workshop_Meta", 5, 150, "paid", "Pre-call workshop",
                "https://go.highticket.io/v/pre-call/pre-call-workshop-meta",
                "Where the numbered objection library plays. The most copyable "
                "asset in the funnel."),
    "forced": ("VSL_05_Forced_consumption_opt-in", 3, 700, "paid",
               "Forced consumption opt-in", "https://go.highticket.io/v/app",
               "A second gate most people never see. He makes you watch before "
               "you can apply."),
    "forced_app": ("VSL_06_Forced_consumption_application", 4, 700, "paid",
                   "Forced consumption application",
                   "https://go.highticket.io/v/application",
                   "The application behind the forced-consumption path."),
    "profit": ("VSL_07_Profit_strategy_session", 5, 700, "paid",
               "Profit strategy session",
               "https://go.highticket.io/v/profit-strategy-session/1?qualified=true",
               "Qualified leads only — the URL literally carries ?qualified=true."),
    "next": ("VSL_08_Next_steps_TY", 6, 400, "paid", "Next steps",
             "https://go.highticket.io/v/next-steps/1",
             "Terminal page. Carries all 20 videos: case studies plus the "
             "objection library plus the 36:56 mastermind overview."),
    "web_optin": ("WEB_01_Webinar_opt-in_VIP", 2, 1620, "ever", "Webinar opt-in",
                  "https://go.highticket.io/w/main/vip/sign-up-vip",
                  "“FREE EVENT @ 8PM ET TONIGHT”. 2,500+ Trustpilot reviews "
                  "in the header."),
    "bridge": ("WEB_02_Bridge_page", 3, 1620, "ever", "Bridge — paid VIP upsell",
               "https://go.highticket.io/w/main/vip/",
               "He sells a paid VIP upgrade BEFORE the event has happened. "
               "Monetises the dead zone Shelby leaves empty."),
    "web_ty": ("WEB_03_Thank-you_page", 4, 1620, "ever", "Thank-you + countdown",
               "https://go.highticket.io/w/main/thank-you",
               "Countdown timer plus the WebinarJam room link. Two-step "
               "confirmation ritual."),
    "checkout": ("WEB_05_Checkout_995", 6, 1620, "ever", "$995 checkout",
                 "https://1orderaway.com/now",
                 "Direct checkout. NO call, no application. $995, 97 spots, "
                 "6 bonuses stacked to $100k+, money-back plus a $500 rebate."),
    "replay": ("WEB_04_Replay_page", 7, 1620, "ever", "Replay room",
               "https://event.webinarjam.com/l319q/replay/",
               "“Closing This Tab Ends The Session.” Not enforced — the "
               "token regenerates a fresh room."),
}

# id -> (col, y, h, lane, kicker, title, rows[], foot)
DATA = {
    "ads": (1, 480, 430, "paid", "TRAFFIC → VSL (HIGH TICKET)", "Meta ads · VSL funnel",
            [("Ads analysed", "585"), ("Still live", "147"),
             ("Facebook pages", "5"), ("Only page that works", "“Brook Hiddink”"),
             ("Credential pages", "0% live")],
            "Every credential-stacked page is dead. The plain-name page carries "
            "347 ads at 39% survival."),
    "ads_web": (1, 1640, 400, "ever", "TRAFFIC → WEBINAR ($995)", "Meta ads · webinar funnel",
                [("Destination", "VIP opt-in"), ("Event", "nightly 8pm ET"),
                 ("Sells", "$995 — direct checkout"),
                 ("No call", "no application"), ("Cap", "97 spots")],
                "A separate lane at a completely different price point. These ads "
                "never touch the high-ticket VSL funnel."),
    "live_room": (5, 1640, 430, "ever", "THE EVENT · LIVE", "Live room",
                  [("Runtime", "2h 14m 40s"), ("Platform", "WebinarJam / Zoom"),
                   ("Title", "Law Student → $5M in 18 months"),
                   ("Cadence", "nightly, 8pm ET"), ("Format", "genuinely live")],
                  "The live room comes FIRST. Replay only exists for the people "
                  "who did not show."),
    "sms": (2, 2620, 430, "event", "ALWAYS ON", "SMS — 3 personas",
            [("Brook (personal)", "(720) 610-3324"),
             ("“Anastasia”, assistant", "(877) 730-9884"),
             ("“Jack”, post-event", "(814) 822-5129"),
             ("Script", "identical every cycle"), ("Email volume", "14 threads only")],
            "Texts constantly as three people. Shelby is the exact inverse: "
            "43 daily emails, zero pre-class SMS."),
    "downsell": (5, 2620, 400, "event", "BACK END", "Downsell ladder",
                 [("Main program", "high ticket"),
                  ("Step down", "Accelerator Lite"),
                  ("Payments", "from $295/month"),
                  ("Channel", "SMS"), ("Deadline", "hard midnight")],
                 "When the main offer does not land, the same text thread walks "
                 "the lead down."),
}



# ---------------------------------------------------------------- routing logic
# Hangs BELOW the clean funnel line. Each entry is a condition and what fires.
# state: "yes" | "no" | "dq" | "unver"  (unver = claimed, not yet proven)
# (id, x, y, state, condition, body, evidence)
BRANCH = [
    ("b_dq", X[2] + 15, 1230, "dq", "VSL application → DQ → the $995 webinar",
     "<b>Confirmed in his own Typeform config.</b> The application "
     "(<code>kfhi4I9N</code>) has six endings, and one of them is literally named "
     "<b>“Disqualified - Webinar”</b>. Fail the money gate and you are not dropped — "
     "you are routed into the $995 offer. His rejects are a product line.",
     "VERIFIED · endings: Tier 1 Call Booking · Tier 2 Call Booking · "
     "Disqualified - Webinar · Thank You Tier 1 · Thank You Tier 2"),
    ("b_gate", X[3] + 15, 1230, "dq", "The gate is $5,000",
     "Three money questions decide it. <b>Investment:</b> “too expensive” / "
     "“no $5,000 but open to financing” / “$5,000+ if everything aligns”. "
     "<b>Credit:</b> below 600 · 600-650 · 650-700 · 700+. <b>Capital:</b> "
     "below $5,000 · $5,000-10,000 · $10,000+. Plus an intent question that DQs "
     "“only gathering information”.",
     "VERIFIED · read from the public form definition, nothing submitted"),
    ("b_qualified", X[5] + 15, 1230, "yes", "VSL application → qualified (2 tiers)",
     "Not one call — <b>two</b>. The form routes to <b>Tier 1 Call Booking</b> or "
     "<b>Tier 2 Call Booking</b> with separate thank-you pages, so the money "
     "answers decide which closer tier you reach. Then a pre-call workshop "
     "carrying the numbered objection library. The URL carries "
     "<code>?qualified=true</code>.",
     "VERIFIED · form endings + captured page 07_Profit_strategy_session"),
    ("b_showed", X[5] + 15, 2200, "yes", "Webinar → made it to the pitch",
     "Gets the replay <b>cut down to the pitch only</b>. No re-teach of the "
     "content they already sat through.",
     "UNVERIFIED · needs a second identity that attends in full"),
    ("b_noshow", X[3] + 15, 2200, "no", "Webinar → did not show",
     "<b>Auto-registered into an ENCORE event about 2.5 hours after the live "
     "room ends.</b> Nobody clicks anything. A fresh Zoom confirmation simply "
     "arrives, and the SMS layer restarts on the new date.",
     "VERIFIED TWICE · 21 Jun 23:45 live → 22 Jun 02:24 encore confirmation · "
     "21 Jul 23:45 live → 22 Jul 02:26 encore confirmation"),
    ("b_retarget", X[1] + 15, 2200, "no", "Everyone → hard retargeting",
     "Registration does not end the ad spend. Retargeting keeps running against "
     "registrants and no-shows, which is why event-urgency creative dominates "
     "his live ads rather than cold-audience hooks.",
     "PARTIALLY VERIFIED · 147 live ads skew heavily to event urgency; the "
     "audience split is not visible in public Ad Library data"),
]


def branch_card(b):
    bid, x, y, state, cond, body, ev = b
    cls = "br " + ("unver" if "UNVERIFIED" in ev else state)
    return (f'<div class="{cls}" style="left:{x}px;top:{y}px">'
            f'<span class="cond">{cond}</span><p>{body}</p>'
            f'<span class="ev">{ev}</span></div>')


A = []
PAID, EVER, EVENT = "#818cf8", "#34d399", "#fb923c"


def b64(rel):
    p = os.path.join(SHOTS_SRC, "brook_" + os.path.basename(rel))
    with open(p, "rb") as fh:
        return "data:image/jpeg;base64," + base64.b64encode(fh.read()).decode()


def node_box(nid):
    if nid in SHOTS:
        asset, col, y = SHOTS[nid][0], SHOTS[nid][1], SHOTS[nid][2]
        return X[col], y, CARD_W, DIMS["assets/%s.jpg" % asset][1] + CHROME
    col, y, h = DATA[nid][0], DATA[nid][1], DATA[nid][2]
    return X[col], y, CARD_W, h


def right(n):
    x, y, w, h = node_box(n); return (x + w, y + h / 2)


def left(n):
    x, y, w, h = node_box(n); return (x, y + h / 2)


def bottom(n):
    x, y, w, h = node_box(n); return (x + w / 2, y + h)


def top(n):
    x, y, w, h = node_box(n); return (x + w / 2, y)


def h_arrow(a, b, col=PAID, label=None):
    (x1, y1), (x2, y2) = right(a), left(b)
    mx = (x1 + x2) / 2
    A.append(("M%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f"
              % (x1 + 6, y1, mx, y1, mx, y2, x2 - 13, y2),
              col, False, label, ((x1 + x2) / 2, min(y1, y2) - 16)))


def v_arrow(a, b, col=EVER, label=None):
    (x1, y1), (x2, y2) = bottom(a), top(b)
    my = (y1 + y2) / 2
    A.append(("M%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f"
              % (x1, y1 + 6, x1, my, x2, my, x2, y2 - 13),
              col, False, label, ((x1 + x2) / 2, (y1 + y2) / 2 - 12)))


# ------- FUNNEL 1: VSL. Self-contained. Never touches the webinar funnel.
h_arrow("ads", "vsl_app", PAID, "these ads only ever buy a VSL view")
h_arrow("vsl_app", "sched")
h_arrow("sched", "confirm")
h_arrow("confirm", "precall")
h_arrow("precall", "next")
v_arrow("vsl_app", "forced", PAID, "second, harder gate — forced consumption")
h_arrow("forced", "forced_app")
h_arrow("forced_app", "profit")
h_arrow("profit", "next")

# ------- FUNNEL 2: WEBINAR. A separate ad lane with its own destination.
# Live room comes BEFORE the replay; the replay only catches no-shows.
h_arrow("web_optin", "bridge", EVER, "paid VIP upsell BEFORE the event")
h_arrow("bridge", "web_ty", EVER)
h_arrow("web_ty", "live_room", EVER, "nightly live room")
h_arrow("live_room", "checkout", EVER, "pitch → direct checkout")
v_arrow("live_room", "replay", EVER, "no-shows only")
h_arrow("ads_web", "web_optin", EVER, "a separate ad lane — never touches the VSL funnel")

# ------- BACK END: the offer goes out after they have watched.
v_arrow("live_room", "downsell", EVENT, "watched → sent the offer")
bx, by = right("replay")
dx, dy = top("downsell")
A.append(("M%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f"
          % (bx + 6, by, bx + 220, by, dx, by, dx, dy - 13),
          EVENT, False, "replay watchers get the same offer", (bx + 200, by - 18)))
v_arrow("web_optin", "sms", EVENT, "SMS fires on registration")


def drop(nid, bx, by, col):
    """A soft dotted line from a funnel card down to its routing-logic card."""
    x, y, w, h = node_box(nid)
    sx, sy = x + w / 2, y + h
    A.append(("M%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f"
              % (sx, sy + 4, sx, (sy + by) / 2, bx + 150, (sy + by) / 2, bx + 150, by - 8),
              col, True, None, (0, 0)))


drop("vsl_app", X[2] + 15, 1230, "#be123c")
drop("sched", X[5] + 15, 1230, EVER)
drop("forced_app", X[3] + 15, 1230, "#be123c")
drop("live_room", X[5] + 15, 2200, EVER)
drop("web_ty", X[3] + 15, 2200, "#f59e0b")
drop("ads_web", X[1] + 15, 2200, "#f59e0b")


# The one real connection between the funnels: DQ drops into the $995 offer.
_dqx, _dqy = X[2] + 165, 1230 + 190
_ckx, _cky = top("checkout")
A.append(("M%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f"
          % (_dqx, _dqy + 8, _dqx, 1500, _ckx - 400, 1500, _ckx, _cky - 13),
          "#be123c", False, "DQ from high ticket → sold the $995 instead",
          (_ckx - 620, 1478)))

BANDS = [
    (125, "1 · VSL FUNNEL — 42 MINUTES INTO AN APPLICATION", PAID),
    (1545, "2 · WEBINAR FUNNEL — SEPARATE ADS, NIGHTLY LIVE EVENT", EVER),
    (2555, "3 · BACK END — SMS + DOWNSELL AFTER THEY WATCH", EVENT),
]

LANE_TAG = {"paid": "VSL", "ever": "WEBINAR", "event": "SMS / BACK END"}


def shot_card(nid):
    asset, col, y, lane, title, url, note = SHOTS[nid]
    a = "assets/%s.jpg" % asset
    w, h = DIMS[a]
    x, yy, cw, ch = node_box(nid)
    return (f'<a class="n {lane}" href="{url}" target="_blank" rel="noopener" '
            f'style="left:{x}px;top:{yy}px;width:{cw}px">'
            f'<div class="nh"><span class="tag">{LANE_TAG[lane]}</span>'
            f'<span class="go">open ↗</span></div>'
            f'<div class="nt">{title}</div><div class="nu">{url}</div>'
            f'<div class="ni" style="height:{h}px"><img src="{b64(a)}" alt=""></div>'
            f'<div class="nn">{note}</div></a>')


def data_card(nid):
    col, y, h, lane, kick, title, rows, foot = DATA[nid]
    x, yy, cw, ch = node_box(nid)
    rs = "".join(f'<div class="dr"><span>{k}</span><b>{v}</b></div>' for k, v in rows)
    return (f'<div class="n {lane}" style="left:{x}px;top:{yy}px;width:{cw}px;'
            f'height:{h}px">'
            f'<div class="nh"><span class="tag">{kick}</span></div>'
            f'<div class="nt">{title}</div><div class="drs">{rs}</div>'
            f'<div class="nn">{foot}</div></div>')


W, H = 3010, 3180
paths = "".join(
    (f'<path d="{d}" stroke="{c}" stroke-width="1.6" fill="none" stroke-dasharray="5 5" '
     f'opacity=".65"/>' if dashed else
     f'<path d="{d}" stroke="{c}" stroke-width="2.5" fill="none" marker-end="url(#a{c[1:]})"/>')
    + (f'<text class="alabel" x="{lx:.0f}" y="{ly:.0f}">{lab}</text>' if lab else "")
    for d, c, dashed, lab, (lx, ly) in A)
markers = "".join(
    f'<marker id="a{c[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
    f'markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="{c}"/></marker>'
    for c in (PAID, EVER, EVENT))
bands = "".join(
    f'<div class="band" style="top:{y - 52}px"><span style="color:{c}">{t}</span></div>'
    for y, t, c in BANDS)
nodes = ("".join(shot_card(n) for n in SHOTS)
         + "".join(data_card(n) for n in DATA)
         + "".join(branch_card(b) for b in BRANCH))

tpl = open(os.path.join(HERE, "board_template.html")).read()
out = (tpl.replace("{{W}}", str(W)).replace("{{H}}", str(H))
          .replace("{{NODES}}", nodes).replace("{{BANDS}}", bands)
          .replace("{{MARKERS}}", markers).replace("{{PATHS}}", paths)
          )
open(os.path.join(HERE, "board.html"), "w").write(out)
print(f"board.html  {len(out)/1024:.0f} KB  ({len(SHOTS)} screenshots, "
      f"{len(DATA)} data cards, {len(A)} wires)")

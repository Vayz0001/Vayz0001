#!/usr/bin/env python3
"""Generate the profile README's SVG assets (light + dark).

Run:  python3 scripts/build.py
Writes assets/*.svg. Plain SVG + CSS only: GitHub strips scripts and external
fonts. Every animation is decorative: content is fully visible without it, each
plays a few times then stops, and prefers-reduced-motion turns it off.
"""
from pathlib import Path
from html import escape

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

THEMES = {
    # Rush Labs palette: cream / deep green ink / muted gold
    "light": dict(bg="#F6EFE3", panel="#EFE6D4", border="#E2D6BF", text="#0A1C16",
                  muted="#4E6157", accent="#8A6A22", ok="#2E7D57", chip="#EAE0CC"),
    "dark": dict(bg="#0A1C16", panel="#07140F", border="#1E3A2F", text="#F3EBDD",
                 muted="#9FB2A6", accent="#D0C090", ok="#6FD3A0", chip="#12291F"),
}

BASE_CSS = f"""
.sans{{font-family:{SANS}}} .mono{{font-family:{MONO}}}
.fx{{opacity:0}}
.pivot{{transform-box:fill-box;transform-origin:center}}
@media (prefers-reduced-motion: reduce){{ *{{animation:none !important}} }}
"""


def svg(w, h, title, body, t, css="", rect=None):
    rx, ry, rw, rh = rect or (0.5, 0.5, w - 1, h - 1)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{escape(title)}"><title>{escape(title)}</title>'
            f'<style>{BASE_CSS}{css}</style>'
            f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="18" fill="{t["bg"]}" stroke="{t["border"]}"/>'
            f'{body}</svg>')


def text(x, y, s, cls, size, fill, weight=400, anchor="start", ls=0, extra=""):
    return (f'<text xml:space="preserve" x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
            f'text-anchor="{anchor}" letter-spacing="{ls}" {extra}>{escape(s)}</text>')


def chips(x, y, items, t, size=12.5, gap=8, pad=11, h=26):
    out, cx = [], x
    for it in items:
        w = len(it) * size * 0.61 + pad * 2
        out.append(f'<rect x="{cx:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="7" fill="{t["chip"]}" stroke="{t["border"]}"/>')
        out.append(text(round(cx + w / 2, 1), y + h / 2 + size * 0.36, it, "mono", size, t["muted"], anchor="middle"))
        cx += w + gap
    return "".join(out), cx


# ── Header ──────────────────────────────────────────────────────────────────
def header(t):
    W, H = 1000, 350
    css = """
    .scan{animation:scan 7s ease-in-out .4s infinite both}
    .cur{animation:blink 1.1s linear infinite both}
    @keyframes scan{0%{transform:translateY(0);opacity:0}5%{opacity:1}34%{transform:translateY(90px);opacity:1}40%,100%{transform:translateY(90px);opacity:0}}
    @keyframes blink{0%,49.9%{opacity:1}50%,99.9%{opacity:0}100%{opacity:1}}
    """
    b = [text(48, 74, "RUSH LABS · FOUNDER & LEAD ENGINEER", "mono", 13, t["accent"], 600, ls=2),
         text(44, 152, "Vayz", "sans", 80, t["text"], 800, ls=-1.5),
         text(48, 196, "Low-latency execution and on-chain", "sans", 20, t["muted"]),
         text(48, 224, "data infrastructure.", "sans", 20, t["muted"])]

    px, py, pw, ph = 560, 40, 392, 196
    b.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="12" fill="{t["panel"]}" stroke="{t["border"]}"/>')
    for i in range(3):
        b.append(f'<circle cx="{px + 22 + i * 16}" cy="{py + 20}" r="4.5" fill="{t["border"]}"/>')
    b.append(text(px + pw - 20, py + 25, "execution-engine", "mono", 12, t["muted"], anchor="end"))
    lx, ly, step = px + 22, py + 60, 30
    b.append(f'<rect class="fx scan" x="{px + 10}" y="{ly - 19}" width="{pw - 20}" height="26" rx="6" fill="{t["accent"]}" fill-opacity=".14"/>')
    b.append(text(lx, ly, "$", "mono", 14, t["accent"], 700) + text(lx + 16, ly, "engine --source mempool", "mono", 14, t["muted"]))
    b.append(text(lx, ly + step, "› pool_create detected", "mono", 14, t["text"]))
    b.append(text(lx, ly + 2 * step, "› pre-built tx submitted", "mono", 14, t["text"])
             + text(px + pw - 22, ly + 2 * step, "< 30 ms", "mono", 14, t["accent"], 700, anchor="end"))
    b.append(text(lx, ly + 3 * step, "› included · same block", "mono", 14, t["text"])
             + text(px + pw - 22, ly + 3 * step, "✓", "mono", 15, t["ok"], 700, anchor="end"))
    b.append(f'<rect class="cur" x="{lx}" y="{ly + 4 * step - 13}" width="9" height="17" fill="{t["accent"]}"/>')

    b.append(f'<line x1="48" y1="262" x2="952" y2="262" stroke="{t["border"]}"/>')
    metrics = [("$10M+", "CUMULATIVE VOLUME"), ("2,500+", "USERS"),
               ("< 30 ms", "MEMPOOL-TO-SUBMIT"), ("Same block", "INCLUSION")]
    col = (952 - 48) / 4
    for i, (v, c) in enumerate(metrics):
        x = 48 + i * col
        if i:
            b.append(f'<line x1="{x - 18:.0f}" y1="282" x2="{x - 18:.0f}" y2="326" stroke="{t["border"]}"/>')
        b.append(text(round(x, 1), 304, v, "sans", 26, t["text"], 750))
        b.append(text(round(x, 1), 326, c, "mono", 11.5, t["muted"], ls=1.5))
    title = ("Vayz — founder and lead engineer at Rush Labs. Low-latency execution and on-chain data "
             "infrastructure. FrenBot: $10M+ cumulative volume, 2,500+ users, under 30 ms mempool-to-submit, "
             "same-block inclusion.")
    return svg(W, H, title, "".join(b), t, css)


# ── Work cards (2-column grid; the gap is drawn inside each SVG so outer edges align) ──
CARDS = [
    ("frenbot", dict(kicker="CARDANO · EXECUTION", period="2024 – 2026", title="FrenBot",
                     desc=["Mempool-driven execution engine in Rust and Go.",
                           "Pre-built transactions, multi-endpoint submission."],
                     stat="$10M+ volume · 2,500+ users · same-block inclusion",
                     chips=["Rust", "Go", "TypeScript", "Ogmios", "Kupo"])),
    ("zing", dict(kicker="CARDANO · ALERTING", period="2024 – now", title="Zing",
                  desc=["Pre-confirmation wallet and pool alerts,",
                        "streamed from the mempool."],
                  stat="1,500+ users · millions of alerts delivered",
                  chips=["Ogmios", "Kupo", "WebSockets", "Firestore"])),
    ("dataapi", dict(kicker="CARDANO · INDEXING", period="2024", title="Chain data API",
                     desc=["Indexed chain data from a self-hosted",
                           "db-sync node: holders, balances, metadata."],
                     stat="Partner APIs for DEXs and aggregators",
                     chips=["Go", "Fiber", "PostgreSQL", "Kupo"])),
    ("launchpad", dict(kicker="CARDANO · LAUNCHPAD", period="2025", title="pump.fren",
                       desc=["Bonding-curve launch backend with a sharded",
                             "transaction pipeline and DEX migration."],
                       stat="6 workers · mint → trade → migrate",
                       chips=["TypeScript", "Bun", "Elysia", "Lucid"])),
    ("polyfarmer", dict(kicker="POLYMARKET · OPEN SOURCE", period="v0.1 · 2026", title="Polyfarmer",
                        desc=["Self-hosted quoting bot for liquidity rewards,",
                              "with per-market risk limits."],
                        stat="Rust · MIT · keys never leave the host",
                        chips=["Rust", "Tokio", "Axum", "htmx"])),
    ("execution", dict(kicker="POLYMARKET · CLIENT", period="private", title="Execution engine",
                       desc=["Event-driven order execution in Rust.",
                             "Pre-built orders fire on trigger."],
                       stat="No order build on the hot path",
                       chips=["Rust", "Polymarket CLOB"])),
]
CARD_W, CARD_H, GAP, PAD_B = 492, 246, 8, 10   # viewBox = (CARD_W + GAP) x (CARD_H + PAD_B)


def motif(kind, t, delay):
    """Small illustration in the title row (x 384-458, y 54-100) with one gentle, finite animation."""
    m, a, bd = t["muted"], t["accent"], t["border"]
    d = f"animation-delay:{delay}s"
    o = []
    if kind == "frenbot":  # chained blocks; our buy lands right after the pool tx
        for i, x in enumerate((384, 410, 436)):
            o.append(f'<rect x="{x}" y="64" width="22" height="22" rx="5" fill="{t["chip"]}" stroke="{bd}"/>')
            if i < 2:
                o.append(f'<line x1="{x + 22}" y1="75" x2="{x + 26}" y2="75" stroke="{bd}" stroke-width="2"/>')
        o.append(f'<rect x="440" y="69" width="14" height="4" rx="1.5" fill="{m}" opacity=".55"/>')
        o.append(f'<rect class="land" style="{d}" x="440" y="77" width="14" height="4" rx="1.5" fill="{a}"/>')
    elif kind == "zing":  # mempool pulse with a ping at the end
        o.append(f'<polyline points="384,76 402,76 410,60 420,92 428,68 434,76 450,76" fill="none" stroke="{a}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>')
        o.append(f'<circle class="fx ping pivot" style="{d}" cx="454" cy="76" r="4" fill="none" stroke="{a}" stroke-width="1.5"/>')
        o.append(f'<circle cx="454" cy="76" r="3.5" fill="{a}"/>')
    elif kind == "polyfarmer":  # order-book ladder; our quote re-quotes
        for i, w in enumerate([22, 32, 44, 0, 56, 40, 28]):
            y = 56 + i * 6.5
            if w == 0:
                o.append(f'<line x1="392" y1="{y + 2}" x2="458" y2="{y + 2}" stroke="{bd}" stroke-dasharray="2 3"/>')
                continue
            cls = f' class="requote" style="{d}"' if i == 4 else ""
            o.append(f'<rect{cls} x="{458 - w}" y="{y}" width="{w}" height="4" rx="1.5" fill="{a if i == 4 else m}" opacity="{1 if i == 4 else .35}"/>')
    elif kind == "execution":  # trigger -> order, with a packet travelling the wire
        o.append(f'<circle cx="392" cy="76" r="8" fill="none" stroke="{a}" stroke-width="2.5"/>')
        o.append(f'<circle cx="392" cy="76" r="2.8" fill="{a}"/>')
        o.append(f'<line x1="404" y1="76" x2="432" y2="76" stroke="{m}" stroke-width="2" stroke-dasharray="3 3"/>')
        o.append(f'<path d="M428 70 L436 76 L428 82" fill="none" stroke="{m}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
        o.append(f'<circle class="fx packet" style="{d}" cx="404" cy="76" r="3" fill="{a}"/>')
        o.append(f'<rect x="440" y="67" width="18" height="18" rx="4" fill="{a}"/>')
    elif kind == "dataapi":  # result table; rows stream in
        for i in range(4):
            y = 58 + i * 10
            for x, w in ((392, 30), (426, 32)):
                hi = i == 0
                o.append(f'<rect x="{x}" y="{y}" width="{w}" height="6" rx="2" fill="{a if hi else m}" opacity="{1 if hi else .35}"/>')
            if i:
                o.append(f'<rect class="fx row" style="animation-delay:{delay + i * .25:.2f}s" x="392" y="{y}" width="66" height="6" rx="2" fill="{a}"/>')
    elif kind == "launchpad":  # stepped bonding curve -> migration; a marker climbs once
        o.append(f'<polyline points="388,96 398,96 398,90 408,90 408,82 418,82 418,72 428,72 428,60 436,60" fill="none" stroke="{a}" stroke-width="2.5" stroke-linejoin="round"/>')
        o.append(f'<line x1="388" y1="100" x2="436" y2="100" stroke="{bd}"/>')
        o.append(f'<path d="M440 60 L448 60 M445 56 L449 60 L445 64" fill="none" stroke="{m}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
        o.append(f'<rect x="451" y="54" width="10" height="12" rx="2.5" fill="{a}"/>')
        o.append(f'<circle class="fx climb" style="{d}" cx="388" cy="96" r="3" fill="{a}"/>')
    return "".join(o)


CARD_CSS = """
.land{animation:land 5s ease-in-out infinite both}
@keyframes land{0%,30%,100%{opacity:1}15%{opacity:.15}}
.ping{animation:ping 3s ease-out infinite both}
@keyframes ping{0%{opacity:.9;transform:scale(1)}55%,100%{opacity:0;transform:scale(3)}}
.requote{animation:requote 5s ease-in-out infinite both}
@keyframes requote{0%,40%,100%{transform:translateX(0)}20%{transform:translateX(-6px)}}
.packet{animation:packet 2.8s ease-in infinite both}
@keyframes packet{0%{opacity:0;transform:translateX(0)}6%{opacity:1}36%{opacity:1;transform:translateX(30px)}42%,100%{opacity:0;transform:translateX(32px)}}
.row{animation:row 4.5s ease-out infinite both}
@keyframes row{0%{opacity:.5}22%,100%{opacity:0}}
.climb{animation:climb 5.5s ease-in-out infinite both}
@keyframes climb{0%{opacity:0;transform:translate(0,0)}4%{opacity:1}9%{transform:translate(10px,-6px)}18%{transform:translate(20px,-14px)}27%{transform:translate(30px,-24px)}36%{opacity:1;transform:translate(42px,-36px)}42%,100%{opacity:0;transform:translate(48px,-36px)}}
"""


def card(c, key, t, side, delay):
    W, H = CARD_W + GAP, CARD_H + PAD_B
    dx = 0 if side == "L" else GAP
    b = [text(32, 44, c["kicker"], "mono", 12, t["accent"], 600, ls=1.5),
         text(CARD_W - 32, 44, c["period"], "mono", 12, t["muted"], anchor="end"),
         text(31, 84, c["title"], "sans", 30, t["text"], 800, ls=-0.5)]
    for i, line in enumerate(c["desc"]):
        b.append(text(32, 118 + i * 22, line, "sans", 15.5, t["muted"]))
    b.append(text(32, 176, c["stat"], "sans", 15, t["text"], 650))
    ch, _ = chips(32, 196, c["chips"], t)
    b.append(ch)
    b.append(text(CARD_W - 32, 215, "↗", "sans", 18, t["accent"], 700, anchor="end"))
    b.append(motif(key, t, delay))
    body = f'<g transform="translate({dx},0)">{"".join(b)}</g>'
    title = f'{c["title"]}: {" ".join(c["desc"])} {c["stat"]}.'
    return svg(W, H, title, body, t, CARD_CSS, rect=(dx + 0.5, 0.5, CARD_W - 1, CARD_H - 1))


# ── Recognition strip ───────────────────────────────────────────────────────
def award(t):
    W, H = 1000, 96
    # flags are "captured" one by one: each pennant runs up its pole (rest state = raised, full colour)
    css = (".pen{animation:raise .55s cubic-bezier(.34,1.56,.64,1) both,wave 6s ease-in-out infinite}"
           "@keyframes wave{0%,14%,100%{transform:translateY(0)}7%{transform:translateY(-2px)}}"
           "@keyframes raise{0%{opacity:.25;transform:translateY(10px)}100%{opacity:1;transform:translateY(0)}}"
           ".count{animation:count .4s ease-out 2.2s both}@keyframes count{0%{opacity:.3}100%{opacity:1}}")
    b = [text(40, 42, "RECOGNITION", "mono", 12, t["accent"], 600, ls=2),
         text(40, 70, "2nd of 47 teams", "sans", 22, t["text"], 750),
         text(222, 70, "BuidlGuidl AI CTF · Devcon 8, Mumbai · Nov 2026", "sans", 16, t["muted"])]
    x0, step = 752, 17
    for i in range(12):
        x = x0 + i * step
        b.append(f'<line x1="{x}" y1="49" x2="{x}" y2="72" stroke="{t["muted"]}" stroke-opacity=".45" stroke-width="1.5" stroke-linecap="round"/>')
        b.append(f'<path class="pen" style="animation-delay:{.6 + i * .11:.2f}s,{2.4 + i * .09:.2f}s" d="M{x + .75} 49.5 L{x + 11} 53.5 L{x + .75} 57.5 Z" fill="{t["accent"]}"/>')
    b.append(text(956, 42, "12 / 12 FLAGS", "mono count", 11.5, t["muted"], anchor="end", ls=1.5))
    title = "Recognition: 2nd of 47 teams, BuidlGuidl AI CTF at Devcon 8, Mumbai, November 2026. 12 of 12 flags captured."
    return svg(W, H, title, "".join(b), t, css)


# ── Stack ───────────────────────────────────────────────────────────────────
STACK = [
    ("SYSTEMS", ["Rust (Tokio, Axum)", "Go (Fiber)", "TypeScript (Bun, Node)"]),
    ("CHAIN", ["Ogmios", "Kupo", "cardano-db-sync", "Lucid", "Polymarket CLOB"]),
    ("DATA", ["PostgreSQL", "Redis", "MongoDB", "Firestore"]),
    ("INFRA", ["Linux", "AWS", "Azure", "PM2", "Self-hosted Cardano nodes"]),
]


def stack(t):
    W, row = 1000, 42
    H = 56 + len(STACK) * row + 18
    span = (len(STACK) - 1) * row
    css = (".sweep{animation:sweep 8s ease-in-out .8s infinite both}"
           f"@keyframes sweep{{0%{{opacity:0;transform:translateY(0)}}4%{{opacity:1}}28%{{opacity:1;transform:translateY({span}px)}}34%,100%{{opacity:0;transform:translateY({span}px)}}}}")
    b = [text(40, 42, "STACK", "mono", 12, t["accent"], 600, ls=2),
         f'<rect class="fx sweep" x="24" y="{62 - 6}" width="952" height="38" rx="8" fill="{t["accent"]}" fill-opacity=".10"/>']
    for i, (label, items) in enumerate(STACK):
        y = 62 + i * row
        b.append(text(40, y + 17, label, "mono", 11.5, t["muted"], ls=1.5))
        ch, _ = chips(170, y, items, t, size=12.5, gap=7, pad=10)
        b.append(ch)
    title = "Stack — " + "; ".join(f'{l.title()}: {", ".join(i)}' for l, i in STACK)
    return svg(W, H, title, "".join(b), t, css)


# ── Status footer ───────────────────────────────────────────────────────────
DISCORD_PATH = "M20.317 4.3698a19.7913 19.7913 0 00-4.8851-1.5152.0741.0741 0 00-.0785.0371c-.211.3753-.4447.8648-.6083 1.2495-1.8447-.2762-3.68-.2762-5.4868 0-.1636-.3933-.4058-.8742-.6177-1.2495a.077.077 0 00-.0785-.037 19.7363 19.7363 0 00-4.8852 1.515.0699.0699 0 00-.0321.0277C.5334 9.0458-.319 13.5799.0992 18.0578a.0824.0824 0 00.0312.0561c2.0528 1.5076 4.0413 2.4228 5.9929 3.0294a.0777.0777 0 00.0842-.0276c.4616-.6304.8731-1.2952 1.226-1.9942a.076.076 0 00-.0416-.1057c-.6528-.2476-1.2743-.5495-1.8722-.8923a.077.077 0 01-.0076-.1277c.1258-.0943.2517-.1923.3718-.2914a.0743.0743 0 01.0776-.0105c3.9278 1.7933 8.18 1.7933 12.0614 0a.0739.0739 0 01.0785.0095c.1202.099.246.1981.3728.2924a.077.077 0 01-.0066.1276 12.2986 12.2986 0 01-1.873.8914.0766.0766 0 00-.0407.1067c.3604.698.7719 1.3628 1.225 1.9932a.076.076 0 00.0842.0286c1.961-.6067 3.9495-1.5219 6.0023-3.0294a.077.077 0 00.0313-.0552c.5004-5.177-.8382-9.6739-3.5485-13.6604a.061.061 0 00-.0312-.0286zM8.02 15.3312c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9555-2.4189 2.157-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.9555 2.4189-2.1569 2.4189zm7.9748 0c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9554-2.4189 2.1569-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.946 2.4189-2.1568 2.4189Z"  # Simple Icons (CC0), 24x24


def footer(t):
    W, H = 1000, 64
    css = (".ring{animation:ring 2.4s ease-out 1s infinite both}"
           "@keyframes ring{0%{opacity:.8;transform:scale(1)}100%{opacity:0;transform:scale(3.2)}}")
    m = t["muted"]
    b = [f'<circle class="fx ring pivot" cx="44" cy="32" r="5" fill="none" stroke="{t["ok"]}" stroke-width="1.5"/>',
         f'<circle cx="44" cy="32" r="5" fill="{t["ok"]}"/>',
         text(62, 37, "Available for contract work", "sans", 15.5, t["text"], 600),
         # discord: icon + handle
         f'<g transform="translate(762,23) scale(.75)"><path d="{DISCORD_PATH}" fill="{m}"/></g>',
         text(788, 37, "vayzzz", "mono", 13.5, m),
         # web: globe icon + domain
         f'<g fill="none" stroke="{m}" stroke-width="1.5" stroke-linecap="round">'
         f'<circle cx="868" cy="32" r="8.5"/><ellipse cx="868" cy="32" rx="3.8" ry="8.5"/><line x1="859.5" y1="32" x2="876.5" y2="32"/></g>',
         text(884, 37, "rushlabs.io", "mono", 13.5, m)]
    title = "Available for contract work. Discord: vayzzz. Web: rushlabs.io"
    return svg(W, H, title, "".join(b), t, css)


# ── Build: version-stamped filenames (bypasses GitHub's image cache) + README ──
import hashlib

files = {}
for name, t in THEMES.items():
    files[f"header-{name}"] = header(t)
    files[f"award-{name}"] = award(t)
    files[f"stack-{name}"] = stack(t)
    files[f"footer-{name}"] = footer(t)
    for i, (key, c) in enumerate(CARDS):
        files[f"card-{key}-{name}"] = card(c, key, t, "L" if i % 2 == 0 else "R", delay=1.0 + i * 0.35)

VER = hashlib.sha1("".join(files[k] for k in sorted(files)).encode()).hexdigest()[:7]
for old in OUT.glob("*.svg"):
    old.unlink()
for stem, content in files.items():
    (OUT / f"{stem}.{VER}.svg").write_text(content)

LINKS = {
    "frenbot": "https://rushlabs.io/work/frenbot",
    "zing": "https://rushlabs.io/work/mempool-alerts",
    "dataapi": "https://rushlabs.io/work/onchain-infrastructure",
    "launchpad": "https://rushlabs.io",
    "polyfarmer": "https://github.com/Vayz0001/polyfarmer",
    "execution": "https://rushlabs.io",
}


def pic(stem, alt, width="100%", href=None):
    p = (f'<picture><source media="(prefers-color-scheme: dark)" srcset="assets/{stem}-dark.{VER}.svg">'
         f'<img alt="{escape(alt)}" src="assets/{stem}-light.{VER}.svg" width="{width}"></picture>')
    return f'<a href="{href}">{p}</a>' if href else p


def alt_of(c):
    return f'{c["title"]}: {" ".join(c["desc"])} {c["stat"]}.'


rows = []
for i in range(0, len(CARDS), 2):
    (ka, ca), (kb, cb) = CARDS[i], CARDS[i + 1]
    # no whitespace between the two cards: exactly 50% + 50% of the README width
    rows.append(pic(f"card-{ka}", alt_of(ca), "50%", LINKS[ka]) + pic(f"card-{kb}", alt_of(cb), "50%", LINKS[kb]))

readme = "\n\n".join([
    pic("header", "Vayz — founder and lead engineer at Rush Labs. Low-latency execution and on-chain data infrastructure. "
                  "FrenBot: $10M+ cumulative volume, 2,500+ users, under 30 ms mempool-to-submit, same-block inclusion."),
    "<p>\n" + "\n".join(rows) + "\n</p>",
    pic("award", "Recognition: 2nd of 47 teams, BuidlGuidl AI CTF at Devcon 8, Mumbai, November 2026. 12 of 12 flags captured.",
        href="https://ctf-mumbai.buidlguidl.com/leaderboard"),
    pic("stack", "Stack. " + " ".join(f'{l.title()}: {", ".join(i)}.' for l, i in STACK)),
    pic("footer", "Available for contract work. Discord: vayzzz. Web: rushlabs.io", href="https://rushlabs.io"),
]) + "\n"
(OUT.parent / "README.md").write_text(readme)
print("version", VER, "·", len(files), "svgs + README.md")

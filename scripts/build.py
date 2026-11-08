#!/usr/bin/env python3
"""Generate the profile README and its SVG assets (light + dark).

Run:  python3 scripts/build.py
Writes assets/*.<hash>.svg (content-hashed names bypass GitHub's image cache)
and README.md. Plain SVG + CSS only: GitHub strips scripts and external fonts.
Animations are decorative and loop with rest periods; content is fully
visible without them, and prefers-reduced-motion switches them off.
"""
from pathlib import Path
from html import escape
import hashlib

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
OUT.mkdir(exist_ok=True)

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

THEMES = {
    # Rush Labs palette: cream / deep green ink / gold. Light accent and muted
    # darkened for WCAG AA on small text (>= 4.5:1 on bg, panel and chips).
    "light": dict(bg="#F6EFE3", panel="#EFE6D4", border="#E2D6BF", text="#0A1C16",
                  muted="#45574D", accent="#735614", ok="#2E7D57", chip="#EAE0CC"),
    "dark": dict(bg="#0A1C16", panel="#07140F", border="#1E3A2F", text="#F3EBDD",
                 muted="#9FB2A6", accent="#D0C090", ok="#6FD3A0", chip="#12291F"),
}
ICON_GREY = "#8B949E"   # GitHub's muted text colour; readable on both themes
PAD = 40                # one left padding for every block

BASE_CSS = f"""
.sans{{font-family:{SANS}}} .mono{{font-family:{MONO}}}
.fx{{opacity:0}}
.pivot{{transform-box:fill-box;transform-origin:center}}
@media (prefers-reduced-motion: reduce){{ *{{animation:none !important}} }}
"""

DISCORD_PATH = "M20.317 4.3698a19.7913 19.7913 0 00-4.8851-1.5152.0741.0741 0 00-.0785.0371c-.211.3753-.4447.8648-.6083 1.2495-1.8447-.2762-3.68-.2762-5.4868 0-.1636-.3933-.4058-.8742-.6177-1.2495a.077.077 0 00-.0785-.037 19.7363 19.7363 0 00-4.8852 1.515.0699.0699 0 00-.0321.0277C.5334 9.0458-.319 13.5799.0992 18.0578a.0824.0824 0 00.0312.0561c2.0528 1.5076 4.0413 2.4228 5.9929 3.0294a.0777.0777 0 00.0842-.0276c.4616-.6304.8731-1.2952 1.226-1.9942a.076.076 0 00-.0416-.1057c-.6528-.2476-1.2743-.5495-1.8722-.8923a.077.077 0 01-.0076-.1277c.1258-.0943.2517-.1923.3718-.2914a.0743.0743 0 01.0776-.0105c3.9278 1.7933 8.18 1.7933 12.0614 0a.0739.0739 0 01.0785.0095c.1202.099.246.1981.3728.2924a.077.077 0 01-.0066.1276 12.2986 12.2986 0 01-1.873.8914.0766.0766 0 00-.0407.1067c.3604.698.7719 1.3628 1.225 1.9932a.076.076 0 00.0842.0286c1.961-.6067 3.9495-1.5219 6.0023-3.0294a.077.077 0 00.0313-.0552c.5004-5.177-.8382-9.6739-3.5485-13.6604a.061.061 0 00-.0312-.0286zM8.02 15.3312c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9555-2.4189 2.157-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.9555 2.4189-2.1569 2.4189zm7.9748 0c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9554-2.4189 2.1569-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.946 2.4189-2.1568 2.4189Z"  # Simple Icons (CC0), 24x24


def svg(w, h, title, body, t, css="", rect=None):
    rx, ry, rw, rh = rect or (0.5, 0.5, w - 1, h - 1)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{escape(title)}"><title>{escape(title)}</title>'
            f'<style>{BASE_CSS}{css}</style>'
            f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="18" fill="{t["bg"]}" stroke="{t["border"]}"/>'
            f'{body}</svg>')


def text(x, y, s, cls, size, fill, weight=400, anchor="start", ls=0, extra=""):
    return (f'<text xml:space="preserve" x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{fill}" '
            f'font-weight="{weight}" text-anchor="{anchor}" letter-spacing="{ls}" {extra}>{escape(s)}</text>')


def chips(x, y, items, t, size=14, gap=8, pad=11, h=28):
    out, cx = [], x
    for it in items:
        w = len(it) * size * 0.61 + pad * 2
        out.append(f'<rect x="{cx:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="7" fill="{t["chip"]}" stroke="{t["border"]}"/>')
        out.append(text(round(cx + w / 2, 1), y + h / 2 + size * 0.36, it, "mono", size, t["muted"], anchor="middle"))
        cx += w + gap
    return "".join(out)


# ── Header ──────────────────────────────────────────────────────────────────
def header(t):
    W, H = 1000, 378
    css = """
    .scan{animation:scan 7s ease-in-out .4s infinite both}
    @keyframes scan{0%{transform:translateY(0);opacity:0}5%{opacity:1}34%{transform:translateY(90px);opacity:1}40%,100%{transform:translateY(90px);opacity:0}}
    .cur{animation:blink 1.1s linear infinite both}
    @keyframes blink{0%,49.9%{opacity:1}50%,99.9%{opacity:0}100%{opacity:1}}
    .ring{animation:ring 2.4s ease-out 1s infinite both}
    @keyframes ring{0%{opacity:.8;transform:scale(1)}100%{opacity:0;transform:scale(3.2)}}
    """
    b = [text(PAD, 72, "RUSH LABS · FOUNDER & LEAD ENGINEER", "sans", 13, t["accent"], 700, ls=1),
         text(PAD - 3, 150, "Vayz", "sans", 80, t["text"], 700, ls=-1.5),
         text(PAD, 194, "Low latency execution and on-chain", "sans", 20, t["muted"]),
         text(PAD, 222, "data infrastructure.", "sans", 20, t["muted"]),
         # availability, pulsing
         f'<circle class="fx ring pivot" cx="{PAD + 6}" cy="256" r="5" fill="none" stroke="{t["ok"]}" stroke-width="1.5"/>',
         f'<circle cx="{PAD + 6}" cy="256" r="5" fill="{t["ok"]}"/>',
         text(PAD + 20, 262, "Available for contract work", "sans", 16, t["text"], 700)]

    px, py, pw, ph = 560, 40, 400, 196
    b.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="12" fill="{t["panel"]}" stroke="{t["border"]}"/>')
    for i in range(3):
        b.append(f'<circle cx="{px + 22 + i * 16}" cy="{py + 20}" r="4.5" fill="{t["border"]}"/>')
    b.append(text(px + pw - 20, py + 25, "frenbot", "mono", 13, t["muted"], anchor="end"))
    lx, ly, step = px + 22, py + 62, 30
    b.append(f'<rect class="fx scan" x="{px + 10}" y="{ly - 19}" width="{pw - 20}" height="26" rx="6" fill="{t["accent"]}" fill-opacity=".14"/>')
    b.append(text(lx, ly, "$", "mono", 14, t["accent"], 700) + text(lx + 16, ly, "frenbot --watch mempool", "mono", 14, t["muted"]))
    b.append(text(lx, ly + step, "› pool_create detected", "mono", 14, t["text"]))
    b.append(text(lx, ly + 2 * step, "› prebuilt tx submitted", "mono", 14, t["text"])
             + text(px + pw - 22, ly + 2 * step, "< 30 ms", "mono", 14, t["accent"], 700, anchor="end"))
    b.append(text(lx, ly + 3 * step, "› included · same block", "mono", 14, t["text"])
             + text(px + pw - 22, ly + 3 * step, "✓", "mono", 15, t["ok"], 700, anchor="end"))
    b.append(f'<rect class="cur" x="{lx}" y="{ly + 4 * step - 13}" width="9" height="17" fill="{t["accent"]}"/>')

    b.append(f'<line x1="{PAD}" y1="290" x2="{W - PAD}" y2="290" stroke="{t["border"]}"/>')
    metrics = [("$10M+", "Cumulative volume"), ("2,500+", "Users"),
               ("< 30 ms", "Reaction time · 100× faster"), ("40+", "Clients since 2021")]
    col = (W - 2 * PAD) / 4
    for i, (v, c) in enumerate(metrics):
        x = PAD + i * col
        if i:
            b.append(f'<line x1="{x - 16:.0f}" y1="308" x2="{x - 16:.0f}" y2="352" stroke="{t["border"]}"/>')
        b.append(text(round(x, 1), 332, v, "sans", 30, t["text"], 700))
        b.append(text(round(x, 1), 354, c, "sans", 15, t["muted"]))
    title = ("Vayz, founder and lead engineer at Rush Labs. Low latency execution and on-chain data infrastructure. "
             "Available for contract work. $10M+ cumulative volume, 2,500+ users, under 30 ms reaction time "
             "(100× faster), 40+ clients since 2021.")
    return svg(W, H, title, "".join(b), t, css)


# ── Work cards: 2 columns; the gap is drawn inside each SVG so outer edges align ──
CARDS = [
    ("frenbot", dict(cat="Cardano · Execution", years="2024–26", title="FrenBot",
                     line="Trades new pools straight from the mempool",
                     tags=["Rust", "Go", "Ogmios"], href="https://rushlabs.io/work/frenbot")),
    ("execution", dict(cat="Polymarket · Execution", years="2025", title="Execution engine",
                       line="Orders prepared in advance, fired on trigger",
                       tags=["Rust", "Polymarket CLOB"], href="https://rushlabs.io/work")),
    ("zing", dict(cat="Cardano · Alerts", years="2024–now", title="Zing",
                  line="Wallet alerts before confirmation · 1,500+ users",
                  tags=["Ogmios", "Kupo", "WebSockets"], href="https://rushlabs.io/work/mempool-alerts")),
    ("polyzing", dict(cat="Polymarket · Alerts", years="2025", title="PolyZing",
                      line="Wallet trade alerts · 100+ users",
                      tags=["Bun", "MongoDB", "WebSockets"], href="https://rushlabs.io/work")),
    ("dataapi", dict(cat="Cardano · Indexing", years="2024", title="Chain data API",
                     line="Indexed chain data · partner APIs for DEXs",
                     tags=["Go", "PostgreSQL", "Kupo"], href="https://rushlabs.io/work/onchain-infrastructure")),
    ("polyfarmer", dict(cat="Polymarket · Open source", years="2026", title="Polyfarmer",
                        line="Open source market maker · keys stay local",
                        tags=["Rust", "Tokio", "Axum"], href="https://github.com/Vayz0001/polyfarmer")),
]
CARD_W, CARD_H, GAP = 488, 196, 24   # viewBox = (CARD_W + GAP/2) x CARD_H ; each card keeps GAP/2 on its inner side


def motif(kind, t, delay):
    """56x56 illustration, top right of the card (x 392-448, y 26-82). Loops gently."""
    m, a, bd = t["muted"], t["accent"], t["border"]
    d = f"animation-delay:{delay}s"
    o = []
    if kind == "frenbot":  # chained blocks; our buy lands right after the pool tx
        for i, x in enumerate((392, 412, 432)):
            o.append(f'<rect x="{x}" y="45" width="17" height="17" rx="4" fill="{t["chip"]}" stroke="{bd}"/>')
        o.append(f'<line x1="409" y1="53.5" x2="412" y2="53.5" stroke="{bd}" stroke-width="2"/>')
        o.append(f'<line x1="429" y1="53.5" x2="432" y2="53.5" stroke="{bd}" stroke-width="2"/>')
        o.append(f'<rect x="435" y="49" width="11" height="3.5" rx="1.5" fill="{m}" opacity=".6"/>')
        o.append(f'<rect class="land" style="{d}" x="435" y="55" width="11" height="3.5" rx="1.5" fill="{a}"/>')
    elif kind == "execution":  # trigger -> order, a packet travels the wire
        o.append(f'<circle cx="398" cy="54" r="7" fill="none" stroke="{a}" stroke-width="2"/>')
        o.append(f'<circle cx="398" cy="54" r="2.5" fill="{a}"/>')
        o.append(f'<line x1="409" y1="54" x2="428" y2="54" stroke="{m}" stroke-width="2" stroke-dasharray="3 3" opacity=".6"/>')
        o.append(f'<path d="M425 49 L431 54 L425 59" fill="none" stroke="{m}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity=".6"/>')
        o.append(f'<circle class="fx packet" style="{d}" cx="409" cy="54" r="2.8" fill="{a}"/>')
        o.append(f'<rect x="434" y="46" width="15" height="15" rx="3.5" fill="{a}"/>')
    elif kind == "zing":  # mempool pulse with a ping
        o.append(f'<polyline points="392,54 404,54 410,40 418,68 424,48 429,54 442,54" fill="none" stroke="{a}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
        o.append(f'<circle class="fx ping pivot" style="{d}" cx="445" cy="54" r="3.5" fill="none" stroke="{a}" stroke-width="1.5"/>')
        o.append(f'<circle cx="445" cy="54" r="3" fill="{a}"/>')
    elif kind == "polyzing":  # fan out to three channels
        o.append(f'<circle cx="398" cy="54" r="5" fill="{a}"/>')
        for i, y in enumerate((36, 54, 72)):
            o.append(f'<line x1="403" y1="54" x2="441" y2="{y}" stroke="{m}" stroke-width="1.5" opacity=".6"/>')
            o.append(f'<circle cx="444" cy="{y}" r="4" fill="none" stroke="{a}" stroke-width="2"/>')
            o.append(f'<circle class="fx fan" style="animation-delay:{delay + i * .18:.2f}s;--dy:{y - 54}px" cx="403" cy="54" r="2.5" fill="{a}"/>')
    elif kind == "dataapi":  # result table, rows stream in
        for i in range(4):
            y = 34 + i * 11
            hi = i == 0
            for x, w in ((392, 26), (422, 26)):
                o.append(f'<rect x="{x}" y="{y}" width="{w}" height="6" rx="2" fill="{a if hi else m}" opacity="{1 if hi else .4}"/>')
            if i:
                o.append(f'<rect class="fx row" style="animation-delay:{delay + i * .25:.2f}s" x="392" y="{y}" width="56" height="6" rx="2" fill="{a}"/>')
    elif kind == "polyfarmer":  # order book ladder; our quote re-quotes
        for i, w in enumerate([18, 28, 38, 0, 50, 34, 22]):
            y = 31 + i * 7
            if w == 0:
                o.append(f'<line x1="398" y1="{y + 2}" x2="448" y2="{y + 2}" stroke="{bd}" stroke-dasharray="2 3"/>')
                continue
            hi = i == 4
            cls = f' class="requote" style="{d}"' if hi else ""
            o.append(f'<rect{cls} x="{448 - w}" y="{y}" width="{w}" height="4" rx="1.5" fill="{a if hi else m}" opacity="{1 if hi else .4}"/>')
    return "".join(o)


CARD_CSS = """
.land{animation:land 5s ease-in-out infinite both}
@keyframes land{0%,30%,100%{opacity:1}15%{opacity:.15}}
.ping{animation:ping 3s ease-out infinite both}
@keyframes ping{0%{opacity:.9;transform:scale(1)}55%,100%{opacity:0;transform:scale(3)}}
.requote{animation:requote 5s ease-in-out infinite both}
@keyframes requote{0%,40%,100%{transform:translateX(0)}20%{transform:translateX(-6px)}}
.packet{animation:packet 2.8s ease-in infinite both}
@keyframes packet{0%{opacity:0;transform:translateX(0)}6%{opacity:1}36%{opacity:1;transform:translateX(19px)}42%,100%{opacity:0;transform:translateX(21px)}}
.row{animation:row 4.5s ease-out infinite both}
@keyframes row{0%{opacity:.5}22%,100%{opacity:0}}
.fan{animation:fan 3.2s ease-in infinite both}
@keyframes fan{0%{opacity:0;transform:translate(0,0)}6%{opacity:1}34%{opacity:1;transform:translate(36px,var(--dy))}40%,100%{opacity:0;transform:translate(38px,var(--dy))}}
"""


def card(c, key, t, side, delay):
    half = GAP // 2
    W, H = CARD_W + half, CARD_H
    dx = 0 if side == "L" else half
    b = [text(PAD, 46, c["cat"], "sans", 14, t["accent"], 700),
         text(PAD, 84, c["title"], "sans", 28, t["text"], 700, ls=-0.4),
         text(PAD, 120, c["line"], "sans", 18, t["muted"]),
         chips(PAD, 142, c["tags"], t),
         text(CARD_W - PAD, 46, c["years"], "mono", 14, t["muted"], anchor="end"),
         f'<g transform="translate(0,22)">{motif(key, t, delay)}</g>']
    body = f'<g transform="translate({dx},0)">{"".join(b)}</g>'
    title = f'{c["title"]} ({c["cat"]}, {c["years"]}): {c["line"]}. {", ".join(c["tags"])}.'
    return svg(W, H, title, body, t, CARD_CSS, rect=(dx + 0.5, 0.5, CARD_W - 1, CARD_H - 1))


# ── Recognition strip ───────────────────────────────────────────────────────
def award(t):
    W, H = 1000, 76
    css = (".pen{animation:raise .55s cubic-bezier(.34,1.56,.64,1) both,wave 6s ease-in-out infinite}"
           "@keyframes raise{0%{opacity:.25;transform:translateY(10px)}100%{opacity:1;transform:translateY(0)}}"
           "@keyframes wave{0%,14%,100%{transform:translateY(0)}7%{transform:translateY(-2px)}}")
    b = [f'<text xml:space="preserve" x="{PAD}" y="45" class="sans" font-size="20" fill="{t["text"]}" font-weight="700">'
         f'2nd of 47 teams<tspan dx="12" font-size="16" font-weight="400" fill="{t["muted"]}">'
         f'BuidlGuidl AI CTF · Devcon 8, Mumbai · 12 of 12 flags</tspan></text>']
    x0, step = W - PAD - 11 * 17 - 11, 17
    for i in range(12):
        x = x0 + i * step
        b.append(f'<line x1="{x}" y1="27" x2="{x}" y2="50" stroke="{t["muted"]}" stroke-opacity=".75" stroke-width="1.5" stroke-linecap="round"/>')
        b.append(f'<path class="pen" style="animation-delay:{.6 + i * .11:.2f}s,{2.4 + i * .09:.2f}s" '
                 f'd="M{x + .75} 27.5 L{x + 11} 31.5 L{x + .75} 35.5 Z" fill="{t["accent"]}"/>')
    title = "2nd of 47 teams, BuidlGuidl AI CTF at Devcon 8, Mumbai, November 2026. 12 of 12 flags captured."
    return svg(W, H, title, "".join(b), t, css)


# ── Phone variants (swapped in under 768px; the README is ~310px wide there) ──
def wrap(s, max_w, size, em=0.53):
    """Greedy word wrap using an average glyph width estimate."""
    lines, cur = [], ""
    for word in s.split(" "):
        if word == "·" and cur:          # never start a line with a separator
            cur += " ·"
            continue
        trial = f"{cur} {word}".strip()
        if len(trial) * size * em <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    return lines + ([cur] if cur else [])


def header_m(t):
    W, H = 400, 418
    css = (".ring{animation:ring 2.4s ease-out 1s infinite both}"
           "@keyframes ring{0%{opacity:.8;transform:scale(1)}100%{opacity:0;transform:scale(3.2)}}")
    P = 24
    b = [text(P, 46, "RUSH LABS · FOUNDER & LEAD ENGINEER", "sans", 14, t["accent"], 700, ls=0.4),
         text(P - 2, 110, "Vayz", "sans", 62, t["text"], 700, ls=-1),
         text(P, 146, "Low latency execution and on-chain", "sans", 19, t["muted"]),
         text(P, 171, "data infrastructure.", "sans", 19, t["muted"]),
         f'<circle class="fx ring pivot" cx="{P + 6}" cy="205" r="5" fill="none" stroke="{t["ok"]}" stroke-width="1.5"/>',
         f'<circle cx="{P + 6}" cy="205" r="5" fill="{t["ok"]}"/>',
         text(P + 20, 211, "Available for contract work", "sans", 17, t["text"], 700),
         f'<line x1="{P}" y1="234" x2="{W - P}" y2="234" stroke="{t["border"]}"/>']
    metrics = [("$10M+", ["Cumulative volume"]), ("2,500+", ["Users"]),
               ("< 30 ms", ["Reaction time", "100× faster"]), ("40+", ["Clients since 2021"])]
    for i, (v, caps) in enumerate(metrics):
        x = P + (i % 2) * 180
        y = 278 + (i // 2) * 76
        b.append(text(x, y, v, "sans", 28, t["text"], 700))
        for j, c in enumerate(caps):
            b.append(text(x, y + 22 + j * 19, c, "sans", 16, t["muted"]))
    title = ("Vayz, founder and lead engineer at Rush Labs. Low latency execution and on-chain data infrastructure. "
             "Available for contract work. $10M+ cumulative volume, 2,500+ users, under 30 ms reaction time "
             "(100× faster), 40+ clients since 2021.")
    return svg(W, H, title, "".join(b), t, css)


CARD_W_M, CARD_H_M, GAP_M = 210, 150, 24


def card_m(c, t, side):
    half = GAP_M // 2
    W, H = CARD_W_M + half, CARD_H_M
    dx = 0 if side == "L" else half
    P = 16
    b = [text(P, 30, c["cat"], "sans", 13, t["accent"], 700),
         text(P, 58, c["title"], "sans", 20, t["text"], 700, ls=-0.3)]
    for i, line in enumerate(wrap(c["line"], CARD_W_M - 2 * P, 16)[:3]):
        b.append(text(P, 86 + i * 20, line, "sans", 16, t["muted"]))
    body = f'<g transform="translate({dx},0)">{"".join(b)}</g>'
    title = f'{c["title"]} ({c["cat"]}, {c["years"]}): {c["line"]}.'
    return svg(W, H, title, body, t, "", rect=(dx + 0.5, 0.5, CARD_W_M - 1, CARD_H_M - 1))


def award_m(t):
    W, H = 400, 96
    css = (".pen{animation:raise .55s cubic-bezier(.34,1.56,.64,1) both,wave 6s ease-in-out infinite}"
           "@keyframes raise{0%{opacity:.25;transform:translateY(10px)}100%{opacity:1;transform:translateY(0)}}"
           "@keyframes wave{0%,14%,100%{transform:translateY(0)}7%{transform:translateY(-2px)}}")
    P = 24
    b = [text(P, 42, "2nd of 47 teams", "sans", 20, t["text"], 700),
         text(P, 70, "BuidlGuidl AI CTF · Devcon 8 · 12 of 12 flags", "sans", 15, t["muted"])]
    step = 12
    x0 = W - P - 11 * step - 9
    for i in range(12):
        x = x0 + i * step
        b.append(f'<line x1="{x}" y1="24" x2="{x}" y2="42" stroke="{t["muted"]}" stroke-opacity=".75" stroke-width="1.3" stroke-linecap="round"/>')
        b.append(f'<path class="pen" style="animation-delay:{.6 + i * .11:.2f}s,{2.4 + i * .09:.2f}s" '
                 f'd="M{x + .65} 24.5 L{x + 9} 27.5 L{x + .65} 30.5 Z" fill="{t["accent"]}"/>')
    title = "2nd of 47 teams, BuidlGuidl AI CTF at Devcon 8, Mumbai, November 2026. 12 of 12 flags captured."
    return svg(W, H, title, "".join(b), t, css)


# ── Footer icons (inline in markdown text) ──────────────────────────────────
def icon_discord():
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" role="img" aria-label="Discord">'
            f'<path d="{DISCORD_PATH}" fill="{ICON_GREY}"/></svg>')


def icon_web():
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" role="img" aria-label="Website">'
            f'<g fill="none" stroke="{ICON_GREY}" stroke-width="2" stroke-linecap="round">'
            f'<circle cx="12" cy="12" r="10"/><ellipse cx="12" cy="12" rx="4.5" ry="10"/><line x1="2" y1="12" x2="22" y2="12"/></g></svg>')


# ── Build ───────────────────────────────────────────────────────────────────
files = {"icon-discord": icon_discord(), "icon-web": icon_web()}
for name, t in THEMES.items():
    files[f"header-{name}"] = header(t)
    files[f"award-{name}"] = award(t)
    files[f"header-m-{name}"] = header_m(t)
    files[f"award-m-{name}"] = award_m(t)
    for i, (key, c) in enumerate(CARDS):
        side = "L" if i % 2 == 0 else "R"
        files[f"card-{key}-{name}"] = card(c, key, t, side, delay=1.0 + i * 0.35)
        files[f"card-m-{key}-{name}"] = card_m(c, t, side)

VER = hashlib.sha1("".join(files[k] for k in sorted(files)).encode()).hexdigest()[:7]
for old in OUT.glob("*.svg"):
    old.unlink()
for stem, content in files.items():
    (OUT / f"{stem}.{VER}.svg").write_text(content)


MOBILE = "(max-width: 767px)"   # verified on github.com: themed-picture keeps width queries intact


def pic(stem, alt, width="100%", href=None, mobile=None):
    """<picture> with light/dark sources, plus phone-sized sources when a mobile stem is given.
    Order matters: the first matching <source> wins."""
    src = ""
    if mobile:
        src += (f'<source media="{MOBILE} and (prefers-color-scheme: dark)" srcset="assets/{mobile}-dark.{VER}.svg">'
                f'<source media="{MOBILE}" srcset="assets/{mobile}-light.{VER}.svg">')
    src += f'<source media="(prefers-color-scheme: dark)" srcset="assets/{stem}-dark.{VER}.svg">'
    p = f'<picture>{src}<img alt="{escape(alt)}" src="assets/{stem}-light.{VER}.svg" width="{width}"></picture>'
    return f'<a href="{href}">{p}</a>' if href else p


def card_alt(c):
    return f'{c["title"]}: {c["line"]}. {", ".join(c["tags"])}.'


blocks = [pic("header", "Vayz, founder and lead engineer at Rush Labs. Low latency execution and on-chain data infrastructure. "
                        "Available for contract work. $10M+ cumulative volume, 2,500+ users, under 30 ms reaction time "
                        "(100× faster), 40+ clients since 2021.", mobile="header-m")]
for i in range(0, len(CARDS), 2):
    (ka, ca), (kb, cb) = CARDS[i], CARDS[i + 1]
    # no whitespace between the two cards: exactly 50% + 50% of the README width
    blocks.append(pic(f"card-{ka}", card_alt(ca), "50%", ca["href"], mobile=f"card-m-{ka}")
                  + pic(f"card-{kb}", card_alt(cb), "50%", cb["href"], mobile=f"card-m-{kb}"))
blocks.append(pic("award", "2nd of 47 teams, BuidlGuidl AI CTF at Devcon 8, Mumbai, November 2026. 12 of 12 flags captured.",
                  href="https://ctf-mumbai.buidlguidl.com/leaderboard", mobile="award-m"))
blocks.append(f'<p align="center">'
              f'<img src="assets/icon-discord.{VER}.svg" height="15" alt="Discord"> <code>vayzzz</code>'
              f'&nbsp;&nbsp;·&nbsp;&nbsp;'
              f'<img src="assets/icon-web.{VER}.svg" height="15" alt="Website"> <a href="https://rushlabs.io">rushlabs.io</a>'
              f'</p>')
(ROOT / "README.md").write_text("\n\n".join(blocks) + "\n")
print("version", VER, "·", len(files), "svgs + README.md")

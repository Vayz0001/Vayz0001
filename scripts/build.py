#!/usr/bin/env python3
"""Generate the profile README's SVG assets (light + dark).

Run:  python3 scripts/build.py
Writes assets/*.svg. Plain SVG + CSS only: GitHub strips scripts and
external fonts, and animations play once and respect reduced motion.
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


def svg(w, h, title, body, t, extra_css=""):
    css = f"""
    .sans{{font-family:{SANS}}} .mono{{font-family:{MONO}}}
    {extra_css}
    @media (prefers-reduced-motion: reduce){{ .l,.cur{{animation:none !important}} }}
    """
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{escape(title)}"><title>{escape(title)}</title>'
            f'<style>{css}</style>'
            f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="18" fill="{t["bg"]}" stroke="{t["border"]}"/>'
            f'{body}</svg>')


def text(x, y, s, cls, size, fill, weight=400, anchor="start", ls=0, extra=""):
    return (f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
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
    anim = """
    .l{animation:scan 2.6s ease-in-out .4s 1 both}
    .cur{animation:blink 1s linear 3s 3 both}
    @keyframes scan{0%{transform:translateY(0);opacity:0}12%{opacity:1}80%{transform:translateY(90px);opacity:1}100%{transform:translateY(90px);opacity:0}}
    @keyframes blink{0%,49.9%{opacity:1}50%,99.9%{opacity:0}100%{opacity:1}}
    """
    b = []
    b.append(text(48, 74, "RUSH LABS · FOUNDER & LEAD ENGINEER", "mono", 13, t["accent"], 600, ls=2))
    b.append(text(44, 152, "Vayz", "sans", 80, t["text"], 800, ls=-1.5))
    b.append(text(48, 196, "Low-latency trading systems, on-chain", "sans", 20, t["muted"]))
    b.append(text(48, 224, "infrastructure, and the dashboards on top.", "sans", 20, t["muted"]))

    # terminal panel
    px, py, pw, ph = 560, 40, 392, 196
    b.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="12" fill="{t["panel"]}" stroke="{t["border"]}"/>')
    for i in range(3):
        b.append(f'<circle cx="{px + 22 + i * 16}" cy="{py + 20}" r="4.5" fill="{t["border"]}"/>')
    b.append(text(px + pw - 20, py + 25, "execution-engine", "mono", 12, t["muted"], anchor="end"))
    lx, ly, step = px + 22, py + 60, 30
    # decorative trace highlight (content below is always visible, even if animation never runs)
    b.append(f'<rect class="l" x="{px + 10}" y="{ly - 19}" width="{pw - 20}" height="26" rx="6" fill="{t["accent"]}" fill-opacity=".14"/>')
    b.append(f'<g>{text(lx, ly, "$", "mono", 14, t["accent"], 700)}'
             f'{text(lx + 16, ly, "engine --watch mempool", "mono", 14, t["muted"])}</g>')
    b.append(f'<g>{text(lx, ly + step, "› pool_create seen in mempool", "mono", 14, t["text"])}</g>')
    b.append(f'<g>{text(lx, ly + 2 * step, "› prebuilt tx submitted", "mono", 14, t["text"])}'
             f'{text(px + pw - 22, ly + 2 * step, "< 30 ms", "mono", 14, t["accent"], 700, anchor="end")}</g>')
    b.append(f'<g>{text(lx, ly + 3 * step, "› included in the same block", "mono", 14, t["text"])}'
             f'{text(px + pw - 22, ly + 3 * step, "✓", "mono", 15, t["ok"], 700, anchor="end")}</g>')
    b.append(f'<rect class="cur" x="{lx}" y="{ly + 4 * step - 13}" width="9" height="17" fill="{t["accent"]}"/>')

    # metrics row
    b.append(f'<line x1="48" y1="262" x2="952" y2="262" stroke="{t["border"]}"/>')
    metrics = [("$10M+", "TRADING VOLUME"), ("2,500+", "TRADERS SERVED"),
               ("< 30 ms", "MEMPOOL → SUBMIT"), ("Same block", "AS POOL CREATION")]
    col = (952 - 48) / 4
    for i, (v, c) in enumerate(metrics):
        x = 48 + i * col
        if i:
            b.append(f'<line x1="{x - 18:.0f}" y1="282" x2="{x - 18:.0f}" y2="326" stroke="{t["border"]}"/>')
        b.append(text(round(x, 1), 304, v, "sans", 26, t["text"], 750))
        b.append(text(round(x, 1), 326, c, "mono", 11.5, t["muted"], ls=1.5))
    title = ("Vayz — founder and lead engineer at Rush Labs. Low-latency trading systems, on-chain infrastructure "
             "and dashboards. FrenBot: $10M+ volume, 2,500+ traders, under 30 ms mempool-to-submission, "
             "buys landing in the same block as pool creation.")
    return svg(W, H, title, "".join(b), t, anim)


# ── Work cards ──────────────────────────────────────────────────────────────
CARDS = {
    "frenbot": dict(kicker="CARDANO · TRADING TERMINAL", period="2024 – 2026", title="FrenBot",
                    desc=["Mempool-native execution engine. Pre-built",
                          "transactions fire the moment a pool appears."],
                    stat="$10M+ volume · 2,500+ traders · same-block buys",
                    chips=["Go", "Rust", "TypeScript", "Ogmios", "Kupo"]),
    "zing": dict(kicker="CARDANO · WALLET ALERTS", period="2024 – now", title="Zing",
                 desc=["Wallet and liquidity alerts streamed from the",
                       "mempool, before block confirmation."],
                 stat="1,500+ users · millions of notifications",
                 chips=["Cardano node", "Ogmios", "Kupo", "Discord"]),
    "polyfarmer": dict(kicker="POLYMARKET · OPEN SOURCE", period="v0.1 · 2026", title="Polyfarmer",
                       desc=["Self-hosted liquidity-rewards engine with",
                             "per-market risk limits and a live dashboard."],
                       stat="Order-book ladder · rewards analytics · encrypted keys",
                       chips=["Rust", "Tokio", "Axum", "htmx"]),
    "execution": dict(kicker="POLYMARKET · CLIENT WORK", period="private", title="Execution engine",
                      desc=["Event-driven order execution. Pre-built",
                            "orders go out the instant a trigger fires."],
                      stat="Sub-millisecond internal trigger-to-order",
                      chips=["Rust", "Polymarket CLOB"]),
}


def motif(kind, t):
    """Small geometric illustration in the title row, right side (x 384-458, y 56-100)."""
    m, a, bd = t["muted"], t["accent"], t["border"]
    o = []
    if kind == "frenbot":  # chained blocks; the last holds the pool tx + our buy
        for i, x in enumerate((384, 410, 436)):
            o.append(f'<rect x="{x}" y="64" width="22" height="22" rx="5" fill="{t["chip"]}" stroke="{bd}"/>')
            if i < 2:
                o.append(f'<line x1="{x + 22}" y1="75" x2="{x + 26}" y2="75" stroke="{bd}" stroke-width="2"/>')
        o.append(f'<rect x="440" y="69" width="14" height="4" rx="1.5" fill="{m}" opacity=".55"/>')
        o.append(f'<rect x="440" y="77" width="14" height="4" rx="1.5" fill="{a}"/>')
    elif kind == "zing":  # mempool pulse
        o.append(f'<polyline points="384,76 402,76 410,60 420,92 428,68 434,76 452,76" fill="none" stroke="{a}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>')
        o.append(f'<circle cx="455" cy="76" r="3.5" fill="{a}"/>')
    elif kind == "polyfarmer":  # order-book ladder, our quote highlighted
        for i, w in enumerate([22, 32, 44, 0, 56, 40, 28]):
            y = 56 + i * 6.5
            if w == 0:
                o.append(f'<line x1="392" y1="{y + 2}" x2="458" y2="{y + 2}" stroke="{bd}" stroke-dasharray="2 3"/>')
                continue
            hi = i == 4
            o.append(f'<rect x="{458 - w}" y="{y}" width="{w}" height="4" rx="1.5" fill="{a if hi else m}" opacity="{1 if hi else .35}"/>')
    elif kind == "execution":  # trigger -> order
        o.append(f'<circle cx="392" cy="76" r="8" fill="none" stroke="{a}" stroke-width="2.5"/>')
        o.append(f'<circle cx="392" cy="76" r="2.8" fill="{a}"/>')
        o.append(f'<line x1="404" y1="76" x2="432" y2="76" stroke="{m}" stroke-width="2" stroke-dasharray="3 3"/>')
        o.append(f'<path d="M428 70 L436 76 L428 82" fill="none" stroke="{m}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
        o.append(f'<rect x="440" y="67" width="18" height="18" rx="4" fill="{a}"/>')
    return "".join(o)


def card(c, key, t):
    W, H = 490, 246
    b = [text(32, 44, c["kicker"], "mono", 12, t["accent"], 600, ls=1.5),
         text(W - 32, 44, c["period"], "mono", 12, t["muted"], anchor="end"),
         text(31, 84, c["title"], "sans", 30, t["text"], 800, ls=-0.5)]
    for i, line in enumerate(c["desc"]):
        b.append(text(32, 118 + i * 22, line, "sans", 15.5, t["muted"]))
    b.append(text(32, 176, c["stat"], "sans", 15, t["text"], 650))
    ch, _ = chips(32, 196, c["chips"], t)
    b.append(ch)
    b.append(text(W - 32, 215, "↗", "sans", 18, t["accent"], 700, anchor="end"))
    b.append(motif(key, t))
    title = f'{c["title"]}: {" ".join(c["desc"])} {c["stat"]}.'
    return svg(W, H, title, "".join(b), t)


# ── Stack ───────────────────────────────────────────────────────────────────
STACK = [
    ("LANGUAGES", ["Rust", "Go", "TypeScript", "JavaScript"]),
    ("BACKEND", ["Tokio", "Axum", "Bun", "Elysia", "WebSockets", "REST"]),
    ("DATA", ["MongoDB", "Redis", "Firebase"]),
    ("FRONTEND", ["Svelte", "htmx", "HTML / CSS"]),
    ("INFRA", ["AWS", "Azure", "Hetzner", "OVH", "DigitalOcean", "Cloudflare", "Vercel", "Linux", "GitHub Actions"]),
    ("WEB3", ["Cardano node", "Ogmios", "Kupo", "Lucid", "Mesh", "EVM", "Solana", "Polymarket CLOB"]),
]


def stack(t):
    W, row = 1000, 42
    H = 56 + len(STACK) * row + 18
    b = [text(40, 42, "STACK", "mono", 12, t["accent"], 600, ls=2)]
    for i, (label, items) in enumerate(STACK):
        y = 62 + i * row
        b.append(text(40, y + 17, label, "mono", 11.5, t["muted"], ls=1.5))
        ch, _ = chips(170, y, items, t, size=12.5, gap=7, pad=10)
        b.append(ch)
    title = "Stack — " + "; ".join(f'{l.title()}: {", ".join(i)}' for l, i in STACK)
    return svg(W, H, title, "".join(b), t)


for name, t in THEMES.items():
    (OUT / f"header-{name}.svg").write_text(header(t))
    (OUT / f"stack-{name}.svg").write_text(stack(t))
    for key, c in CARDS.items():
        (OUT / f"card-{key}-{name}.svg").write_text(card(c, key, t))

print("wrote", sorted(p.name for p in OUT.glob("*.svg")))

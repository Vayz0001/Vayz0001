#!/usr/bin/env python3
"""Generate the personal profile README and its SVG assets (light + dark).
The products live on the rushlabs-ai org profile, so this page is about the person.

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

# One spacing system for every block. PAD is the inset on all four sides: the
# first cap height starts PAD below the top edge and the last baseline (or chip
# edge) sits PAD above the bottom. Every eyebrow sits on the same baseline and
# the next element starts GAP below it, so the blocks line up as one set.
PAD, PAD_M = 40, 28                 # desktop (1000 wide) / phone (400 wide)
EYEBROW_Y, EYEBROW_Y_M = 50, 38     # eyebrow baseline: PAD + cap height
GAP, GAP_M = 20, 19                 # eyebrow baseline -> top of next element
CAPTION_W = 220                     # metric caption measure, desktop and phone

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


def chip_w(s, size, pad):
    return len(s) * size * 0.61 + pad * 2


def chips(x, y, items, t, size=14, gap=8, pad=11, h=28):
    out, cx = [], x
    for it in items:
        w = chip_w(it, size, pad)
        out.append(f'<rect x="{cx:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="7" fill="{t["chip"]}" stroke="{t["border"]}"/>')
        out.append(text(round(cx + w / 2, 1), y + h / 2 + size * 0.36, it, "mono", size, t["muted"], anchor="middle"))
        cx += w + gap
    return "".join(out)


def chip_rows(items, max_w, size, gap, pad):
    """Split chips into rows that fit within max_w, balanced like wrap()."""
    def greedy(limit):
        rows, cur, w = [], [], 0
        for it in items:
            cw = chip_w(it, size, pad)
            if cur and w + gap + cw > limit:
                rows.append(cur)
                cur, w = [], 0
            w += (gap if cur else 0) + cw
            cur.append(it)
        return rows + [cur] if cur else rows

    n, w = len(greedy(max_w)), max_w
    while w > 1 and len(greedy(w - 1)) == n:
        w -= 1
    return greedy(w)


def eyebrow(x, y, s, t, size=14):
    return text(x, y, s, "sans", size, t["accent"], 700, ls=1.2)


def est(s, size, em=0.53):
    """Conservative text width estimate (sans 0.53em, bold sans 0.58em, mono 0.61em)."""
    return len(s) * size * em


def spread(widths, x0, x1):
    """Left edges for columns of the given widths, with equal gutters, filling x0..x1."""
    gap = (x1 - x0 - sum(widths)) / (len(widths) - 1)
    xs, x = [], x0
    for w in widths:
        xs.append(x)
        x += w + gap
    return xs


# ── Header ──────────────────────────────────────────────────────────────────
HEADER_ALT = ("Vayz, founder of Rush Labs. Systems engineer building fast, local AI search. "
              "Rust, Go, TypeScript and Python. Shipping production systems since 2021, "
              "5 open-source releases, NVIDIA Inception member.")
TAGLINE = ("Systems engineer building fast,", "local AI search.")
STATUS = "Building in the open"
METRICS = [("5 yrs", ["Shipping production", "systems"]), ("5", ["Open-source releases"]),
           ("9 of 11", ["BEIR sets where Rush", "Small beats its base"]), ("NVIDIA", ["Inception member"])]


def header(t):
    W = 1000
    px, py, pw, ph = 560, PAD, 400, 200      # terminal panel
    lx, ly, step = px + 22, py + 67, 28      # terminal text origin and line pitch
    css = f"""
    .scan{{animation:scan 7s ease-in-out .4s infinite both}}
    @keyframes scan{{0%{{transform:translateY(0);opacity:0}}5%{{opacity:1}}34%{{transform:translateY({3 * step}px);opacity:1}}40%,100%{{transform:translateY({3 * step}px);opacity:0}}}}
    .cur{{animation:blink 1.1s linear infinite both}}
    @keyframes blink{{0%,49.9%{{opacity:1}}50%,99.9%{{opacity:0}}100%{{opacity:1}}}}
    .ring{{animation:ring 2.4s ease-out 1s infinite both}}
    @keyframes ring{{0%{{opacity:.8;transform:scale(1)}}100%{{opacity:0;transform:scale(3.2)}}}}
    """
    # Left column ends on the status line, level with the terminal's bottom edge (240).
    b = [eyebrow(PAD, EYEBROW_Y, "FOUNDER · RUSH LABS", t),
         text(PAD - 3, 131, "Vayz", "sans", 80, t["text"], 700, ls=-1.5),
         text(PAD, 172, TAGLINE[0], "sans", 20, t["muted"]),
         text(PAD, 200, TAGLINE[1], "sans", 20, t["muted"]),
         f'<circle class="fx ring pivot" cx="{PAD + 6}" cy="234" r="5" fill="none" stroke="{t["ok"]}" stroke-width="1.5"/>',
         f'<circle cx="{PAD + 6}" cy="234" r="5" fill="{t["ok"]}"/>',
         text(PAD + 20, 240, STATUS, "sans", 16, t["text"], 700)]

    b.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="12" fill="{t["panel"]}" stroke="{t["border"]}"/>')
    for i in range(3):
        b.append(f'<circle cx="{px + 22 + i * 16}" cy="{py + 20}" r="4.5" fill="{t["border"]}"/>')
    b.append(text(px + pw - 20, py + 25, "~", "mono", 13, t["muted"], anchor="end"))
    b.append(f'<line x1="{px}" y1="{py + 40}" x2="{px + pw}" y2="{py + 40}" stroke="{t["border"]}"/>')
    b.append(f'<rect class="fx scan" x="{px + 10}" y="{ly - 18}" width="{pw - 20}" height="25" rx="6" fill="{t["accent"]}" fill-opacity=".14"/>')
    b.append(text(lx, ly, "$", "mono", 14, t["accent"], 700) + text(lx + 16, ly, "whoami", "mono", 14, t["muted"]))
    b.append(text(lx, ly + step, "› vayz · founder, rush labs", "mono", 14, t["text"]))
    b.append(text(lx, ly + 2 * step, "› rust · go · typescript · python", "mono", 14, t["text"]))
    b.append(text(lx, ly + 3 * step, "› now: rerankers, local search", "mono", 14, t["text"])
             + text(px + pw - 22, ly + 3 * step, "✓", "mono", 15, t["ok"], 700, anchor="end"))
    b.append(f'<rect class="cur" x="{lx}" y="{ly + 4 * step - 13}" width="9" height="17" fill="{t["accent"]}"/>')

    # Metrics: columns sized to their content with equal gutters, so the long
    # captions get the room they need and none wraps into a neighbour.
    rule, vy, lh = 276, 326, 20
    caps = [wrap(" ".join(c), CAPTION_W, 15) for _, c in METRICS]
    widths = [max(est(v, 30, 0.58), *(est(c, 15) for c in cs)) for (v, _), cs in zip(METRICS, caps)]
    xs = spread(widths, PAD, W - PAD)
    last = vy + 24 + lh * (max(map(len, caps)) - 1)
    H = last + PAD
    b.append(f'<line x1="{PAD}" y1="{rule}" x2="{W - PAD}" y2="{rule}" stroke="{t["border"]}"/>')
    for i, ((v, _), cs, x) in enumerate(zip(METRICS, caps, xs)):
        if i:
            sx = round(x - 28)
            b.append(f'<line x1="{sx}" y1="{rule + 26}" x2="{sx}" y2="{last + 4}" stroke="{t["border"]}"/>')
        b.append(text(round(x, 1), vy, v, "sans", 30, t["text"], 700))
        for j, c in enumerate(cs):
            b.append(text(round(x, 1), vy + 24 + j * lh, c, "sans", 15, t["muted"]))
    return svg(W, H, HEADER_ALT, "".join(b), t, css)


# ── The lab: one wide card that sends people to the org profile ─────────────
LAB = dict(href="https://github.com/rushlabs-ai", url="github.com/rushlabs-ai",
           line="An applied AI lab: open-source models and tools for search, retrieval and local inference.",
           tags=["rerankers", "local search", "fine-tuning", "open models"])
LAB_ALT = "Building Rush Labs. " + LAB["line"] + " github.com/rushlabs-ai"
LAB_CSS = (".nudge{animation:nudge 3.2s ease-in-out 1s infinite both}"
           "@keyframes nudge{0%,60%,100%{transform:translateX(0)}30%{transform:translateX(6px)}}")


def lab(t):
    W, H = 1000, 210
    b = [eyebrow(PAD, EYEBROW_Y, "BUILDING", t),
         text(PAD, 92, "Rush Labs", "sans", 30, t["text"], 700, ls=-0.4),
         f'<g class="nudge"><path d="M{PAD + 172} 82 L{PAD + 188} 82 M{PAD + 181} 75 L{PAD + 188} 82 L{PAD + 181} 89" '
         f'fill="none" stroke="{t["accent"]}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></g>',
         text(PAD, 124, LAB["line"], "sans", 17, t["muted"]),
         chips(PAD, H - PAD - 28, LAB["tags"], t),
         text(W - PAD, EYEBROW_Y, LAB["url"], "mono", 14, t["muted"], anchor="end")]
    return svg(W, H, LAB_ALT, "".join(b), t, LAB_CSS)


def lab_m(t):
    W, P, lh = 400, PAD_M, 22
    size, gap, pad, h = 13, 8, 10, 26
    lines = wrap(LAB["line"], W - 2 * P, 16)
    rows = chip_rows(LAB["tags"], W - 2 * P, size, gap, pad)
    top = 104 + lh * (len(lines) - 1) + 18
    H = top + len(rows) * (h + gap) - gap + P
    b = [eyebrow(P, EYEBROW_Y_M, "BUILDING", t, 13),
         text(W - P, EYEBROW_Y_M, LAB["url"], "mono", 13, t["muted"], anchor="end"),
         text(P, 74, "Rush Labs →", "sans", 24, t["text"], 700, ls=-0.3)]
    for i, line in enumerate(lines):
        b.append(text(P, 104 + i * lh, line, "sans", 16, t["muted"]))
    for i, row in enumerate(rows):
        b.append(chips(P, top + i * (h + gap), row, t, size, gap, pad, h))
    return svg(W, H, LAB_ALT, "".join(b), t)


# ── Path: three steps, oldest first ─────────────────────────────────────────
PATH = [("2021", "Product analyst", "Payments software for banks"),
        ("2021–26", "Systems engineer", "Low-latency trading systems, Rust and Go"),
        ("2026–now", "Founder, Rush Labs", "Open-source AI search, NVIDIA Inception")]
PATH_ALT = "Path: " + " ".join(f"{y}, {r}: {d}." for y, r, d in PATH)
PATH_CSS = (".now{animation:now 2.4s ease-out 1s infinite both}"
            "@keyframes now{0%{opacity:.8;transform:scale(1)}100%{opacity:0;transform:scale(3)}}")


def path(t):
    W, H, dot = 1000, 204, EYEBROW_Y + GAP + 6
    # Columns sized to their text with equal gutters: the long middle line no
    # longer runs up against the last column, and the last one clears the edge.
    widths = [max(est(y, 14, 0.61), est(r, 19, 0.58), est(d, 15)) for y, r, d in PATH]
    xs = spread(widths, PAD, W - PAD)
    b = [eyebrow(PAD, EYEBROW_Y, "PATH", t),
         f'<line x1="{xs[0] + 6:.0f}" y1="{dot}" x2="{xs[-1] + 6:.0f}" y2="{dot}" stroke="{t["border"]}" stroke-width="2"/>']
    for i, ((year, role, desc), x) in enumerate(zip(PATH, xs)):
        last = i == len(PATH) - 1
        if last:
            b.append(f'<circle class="fx now pivot" cx="{x + 6:.0f}" cy="{dot}" r="6" fill="none" stroke="{t["ok"]}" stroke-width="1.5"/>')
        b.append(f'<circle cx="{x + 6:.0f}" cy="{dot}" r="6" fill="{t["ok"] if last else t["border"]}"/>')
        b.append(text(round(x, 1), 112, year, "mono", 14, t["muted"]))
        b.append(text(round(x, 1), 140, role, "sans", 19, t["text"], 700))
        b.append(text(round(x, 1), H - PAD, desc, "sans", 15, t["muted"]))
    return svg(W, H, PATH_ALT, "".join(b), t, PATH_CSS)


def path_m(t):
    W, P, tx, lh = 400, PAD_M, PAD_M + 24, 20
    rows, y = [], EYEBROW_Y_M + GAP_M + 6
    for year, role, desc in PATH:
        lines = wrap(desc, W - P - tx, 15)
        rows.append((y, f"{year} · {role}", lines))
        y += 62 + lh * (len(lines) - 1)
    last_y, _, last_lines = rows[-1]
    H = last_y + 29 + lh * (len(last_lines) - 1) + P
    b = [eyebrow(P, EYEBROW_Y_M, "PATH", t, 13),
         f'<line x1="{P + 6}" y1="{rows[0][0]}" x2="{P + 6}" y2="{last_y}" stroke="{t["border"]}" stroke-width="2"/>']
    for i, (y, head, lines) in enumerate(rows):
        last = i == len(rows) - 1
        if last:
            b.append(f'<circle class="fx now pivot" cx="{P + 6}" cy="{y}" r="6" fill="none" stroke="{t["ok"]}" stroke-width="1.5"/>')
        b.append(f'<circle cx="{P + 6}" cy="{y}" r="6" fill="{t["ok"] if last else t["border"]}"/>')
        b.append(text(tx, y + 6, head, "sans", 17, t["text"], 700))
        for j, line in enumerate(lines):
            b.append(text(tx, y + 29 + j * lh, line, "sans", 15, t["muted"]))
    return svg(W, H, PATH_ALT, "".join(b), t, PATH_CSS)


# ── Recognition strip ───────────────────────────────────────────────────────
def award(t):
    W, H, base = 1000, 96, 56
    css = (".pen{animation:raise .55s cubic-bezier(.34,1.56,.64,1) both,wave 6s ease-in-out infinite}"
           "@keyframes raise{0%{opacity:.25;transform:translateY(10px)}100%{opacity:1;transform:translateY(0)}}"
           "@keyframes wave{0%,14%,100%{transform:translateY(0)}7%{transform:translateY(-2px)}}")
    b = [f'<text xml:space="preserve" x="{PAD}" y="{base}" class="sans" font-size="20" fill="{t["text"]}" font-weight="700">'
         f'2nd of 47 teams<tspan dx="12" font-size="16" font-weight="400" fill="{t["muted"]}">'
         f'BuidlGuidl AI CTF · Devcon 8, Mumbai · 12 of 12 flags</tspan></text>']
    x0, step, top = W - PAD - 11 * 17 - 11, 17, base - 18
    for i in range(12):
        x = x0 + i * step
        b.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{top + 23}" stroke="{t["muted"]}" stroke-opacity=".75" stroke-width="1.5" stroke-linecap="round"/>')
        b.append(f'<path class="pen" style="animation-delay:{.6 + i * .11:.2f}s,{2.4 + i * .09:.2f}s" '
                 f'd="M{x + .75} {top + .5} L{x + 11} {top + 4.5} L{x + .75} {top + 8.5} Z" fill="{t["accent"]}"/>')
    title = "2nd of 47 teams, BuidlGuidl AI CTF at Devcon 8, Mumbai, November 2026. 12 of 12 flags captured."
    return svg(W, H, title, "".join(b), t, css)


# ── Phone variants (swapped in under 768px; the README is ~310px wide there) ──
def wrap(s, max_w, size, em=0.53):
    """Word wrap using an average glyph width estimate. Runs of capitalised
    words (names such as "Rush Small") stay on one line, and the measure is
    then narrowed as far as the line count allows, so lines come out balanced."""
    units = []
    for word in s.split(" "):
        prev = units[-1] if units else ""
        if word == "·" and units:        # never start a line with a separator
            units[-1] += " ·"
        elif word[:1].isupper() and prev[:1].isupper() and prev[-1] not in ",.:;·":
            units[-1] += " " + word
        else:
            units.append(word)

    def greedy(w):
        lines, cur = [], ""
        for u in units:
            trial = f"{cur} {u}".strip()
            if not cur or est(trial, size, em) <= w:
                cur = trial
            else:
                lines.append(cur)
                cur = u
        return lines + ([cur] if cur else [])

    n, w = len(greedy(max_w)), max_w
    while w > 1 and len(greedy(w - 1)) == n:
        w -= 1
    return greedy(w)


def header_m(t):
    W, P = 400, PAD_M
    css = (".ring{animation:ring 2.4s ease-out 1s infinite both}"
           "@keyframes ring{0%{opacity:.8;transform:scale(1)}100%{opacity:0;transform:scale(3.2)}}")
    b = [eyebrow(P, EYEBROW_Y_M, "FOUNDER · RUSH LABS", t, 13),
         text(P - 2, 102, "Vayz", "sans", 62, t["text"], 700, ls=-1),
         text(P, 137, TAGLINE[0], "sans", 19, t["muted"]),
         text(P, 163, TAGLINE[1], "sans", 19, t["muted"]),
         f'<circle class="fx ring pivot" cx="{P + 6}" cy="191" r="5" fill="none" stroke="{t["ok"]}" stroke-width="1.5"/>',
         f'<circle cx="{P + 6}" cy="191" r="5" fill="{t["ok"]}"/>',
         text(P + 20, 197, STATUS, "sans", 17, t["text"], 700),
         f'<line x1="{P}" y1="221" x2="{W - P}" y2="221" stroke="{t["border"]}"/>']
    # One metric per row, value left and caption right, so each caption gets the
    # same measure as on desktop and wraps the same way.
    cx, y, lh = W - P - CAPTION_W, 264, 20
    for v, caps in METRICS:
        lines = wrap(" ".join(caps), CAPTION_W, 15)
        b.append(text(P, y, v, "sans", 26, t["text"], 700))
        for j, c in enumerate(lines):
            b.append(text(cx, y + j * lh, c, "sans", 15, t["muted"]))
        last = y + lh * (len(lines) - 1)
        y = last + 40
    return svg(W, last + P, HEADER_ALT, "".join(b), t, css)


def award_m(t):
    W, P, base, lh = 400, PAD_M, 43, 20
    css = (".pen{animation:raise .55s cubic-bezier(.34,1.56,.64,1) both,wave 6s ease-in-out infinite}"
           "@keyframes raise{0%{opacity:.25;transform:translateY(10px)}100%{opacity:1;transform:translateY(0)}}"
           "@keyframes wave{0%,14%,100%{transform:translateY(0)}7%{transform:translateY(-2px)}}")
    lines = wrap("BuidlGuidl AI CTF · Devcon 8 · 12 of 12 flags", W - 2 * P, 14)
    H = base + 26 + lh * (len(lines) - 1) + P
    b = [text(P, base, "2nd of 47 teams", "sans", 20, t["text"], 700)]
    for i, line in enumerate(lines):
        b.append(text(P, base + 26 + i * lh, line, "sans", 14, t["muted"]))
    step, top = 12, base - 18
    x0 = W - P - 11 * step - 9
    for i in range(12):
        x = x0 + i * step
        b.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{top + 18}" stroke="{t["muted"]}" stroke-opacity=".75" stroke-width="1.3" stroke-linecap="round"/>')
        b.append(f'<path class="pen" style="animation-delay:{.6 + i * .11:.2f}s,{2.4 + i * .09:.2f}s" '
                 f'd="M{x + .65} {top + .5} L{x + 9} {top + 3.5} L{x + .65} {top + 6.5} Z" fill="{t["accent"]}"/>')
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
    for stem, fn in (("header", header), ("lab", lab), ("path", path), ("award", award),
                     ("header-m", header_m), ("lab-m", lab_m), ("path-m", path_m), ("award-m", award_m)):
        files[f"{stem}-{name}"] = fn(t)

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


blocks = [pic("header", HEADER_ALT, mobile="header-m"),
          pic("lab", LAB_ALT, href=LAB["href"], mobile="lab-m"),
          pic("path", PATH_ALT, mobile="path-m"),
          pic("award", "2nd of 47 teams, BuidlGuidl AI CTF at Devcon 8, Mumbai, November 2026. 12 of 12 flags captured.",
              href="https://ctf-mumbai.buidlguidl.com/leaderboard", mobile="award-m"),
          f'<p align="center">'
          f'<img src="assets/icon-discord.{VER}.svg" height="15" alt="Discord"> <code>vayzzz</code>'
          f'&nbsp;&nbsp;·&nbsp;&nbsp;'
          f'<img src="assets/icon-web.{VER}.svg" height="15" alt="Website"> <a href="https://rushlabs.ai">rushlabs.ai</a>'
          f'</p>']
(ROOT / "README.md").write_text("\n\n".join(blocks) + "\n")
print("version", VER, "·", len(files), "svgs + README.md")

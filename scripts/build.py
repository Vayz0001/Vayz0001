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
HEADER_ALT = ("Vayz, founder of Rush Labs. Systems engineer building fast, local AI search. "
              "Rust, Go, TypeScript and Python. Shipping production systems since 2021, "
              "5 open-source releases, NVIDIA Inception member.")
TAGLINE = ("Systems engineer building fast,", "local AI search.")
STATUS = "Building in the open"
METRICS = [("5 yrs", ["Shipping production", "systems"]), ("5", ["Open-source releases"]),
           ("9 of 11", ["BEIR sets where Rush", "Small beats its base"]), ("NVIDIA", ["Inception member"])]


def header(t):
    W, H = 1000, 398
    css = """
    .scan{animation:scan 7s ease-in-out .4s infinite both}
    @keyframes scan{0%{transform:translateY(0);opacity:0}5%{opacity:1}34%{transform:translateY(90px);opacity:1}40%,100%{transform:translateY(90px);opacity:0}}
    .cur{animation:blink 1.1s linear infinite both}
    @keyframes blink{0%,49.9%{opacity:1}50%,99.9%{opacity:0}100%{opacity:1}}
    .ring{animation:ring 2.4s ease-out 1s infinite both}
    @keyframes ring{0%{opacity:.8;transform:scale(1)}100%{opacity:0;transform:scale(3.2)}}
    """
    b = [text(PAD, 72, "FOUNDER · RUSH LABS", "sans", 13, t["accent"], 700, ls=1),
         text(PAD - 3, 150, "Vayz", "sans", 80, t["text"], 700, ls=-1.5),
         text(PAD, 194, TAGLINE[0], "sans", 20, t["muted"]),
         text(PAD, 222, TAGLINE[1], "sans", 20, t["muted"]),
         f'<circle class="fx ring pivot" cx="{PAD + 6}" cy="256" r="5" fill="none" stroke="{t["ok"]}" stroke-width="1.5"/>',
         f'<circle cx="{PAD + 6}" cy="256" r="5" fill="{t["ok"]}"/>',
         text(PAD + 20, 262, STATUS, "sans", 16, t["text"], 700)]

    px, py, pw, ph = 560, 40, 400, 196
    b.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="12" fill="{t["panel"]}" stroke="{t["border"]}"/>')
    for i in range(3):
        b.append(f'<circle cx="{px + 22 + i * 16}" cy="{py + 20}" r="4.5" fill="{t["border"]}"/>')
    b.append(text(px + pw - 20, py + 25, "~", "mono", 13, t["muted"], anchor="end"))
    lx, ly, step = px + 22, py + 62, 30
    b.append(f'<rect class="fx scan" x="{px + 10}" y="{ly - 19}" width="{pw - 20}" height="26" rx="6" fill="{t["accent"]}" fill-opacity=".14"/>')
    b.append(text(lx, ly, "$", "mono", 14, t["accent"], 700) + text(lx + 16, ly, "whoami", "mono", 14, t["muted"]))
    b.append(text(lx, ly + step, "› vayz · founder, rush labs", "mono", 14, t["text"]))
    b.append(text(lx, ly + 2 * step, "› rust · go · typescript · python", "mono", 14, t["text"]))
    b.append(text(lx, ly + 3 * step, "› now: rerankers, local search", "mono", 14, t["text"])
             + text(px + pw - 22, ly + 3 * step, "✓", "mono", 15, t["ok"], 700, anchor="end"))
    b.append(f'<rect class="cur" x="{lx}" y="{ly + 4 * step - 13}" width="9" height="17" fill="{t["accent"]}"/>')

    b.append(f'<line x1="{PAD}" y1="290" x2="{W - PAD}" y2="290" stroke="{t["border"]}"/>')
    col = (W - 2 * PAD) / 4
    for i, (v, caps) in enumerate(METRICS):
        x = PAD + i * col
        if i:
            b.append(f'<line x1="{x - 16:.0f}" y1="308" x2="{x - 16:.0f}" y2="372" stroke="{t["border"]}"/>')
        b.append(text(round(x, 1), 332, v, "sans", 30, t["text"], 700))
        for j, c in enumerate(caps):
            b.append(text(round(x, 1), 354 + j * 19, c, "sans", 15, t["muted"]))
    return svg(W, H, HEADER_ALT, "".join(b), t, css)


# ── The lab: one wide card that sends people to the org profile ─────────────
LAB = dict(href="https://github.com/rushlabs-ai", url="github.com/rushlabs-ai",
           line="An applied AI lab: open-source models and tools for search, retrieval and local inference.",
           tags=["rerankers", "local search", "fine-tuning", "open models"])
LAB_ALT = "Building Rush Labs. " + LAB["line"] + " github.com/rushlabs-ai"
LAB_CSS = (".nudge{animation:nudge 3.2s ease-in-out 1s infinite both}"
           "@keyframes nudge{0%,60%,100%{transform:translateX(0)}30%{transform:translateX(6px)}}")


def lab(t):
    W, H = 1000, 184
    b = [text(PAD, 46, "BUILDING", "sans", 14, t["accent"], 700, ls=1),
         text(PAD, 86, "Rush Labs", "sans", 30, t["text"], 700, ls=-0.4),
         f'<g class="nudge"><path d="M{PAD + 172} 76 L{PAD + 188} 76 M{PAD + 181} 69 L{PAD + 188} 76 L{PAD + 181} 83" '
         f'fill="none" stroke="{t["accent"]}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></g>',
         text(PAD, 118, LAB["line"], "sans", 17, t["muted"]),
         chips(PAD, 132, LAB["tags"], t),
         text(W - PAD, 46, LAB["url"], "mono", 14, t["muted"], anchor="end")]
    return svg(W, H, LAB_ALT, "".join(b), t, LAB_CSS)


def lab_m(t):
    W, P = 400, 24
    lines = wrap(LAB["line"], W - 2 * P, 16)
    H = 104 + len(lines) * 21
    b = [text(P, 40, "BUILDING", "sans", 13, t["accent"], 700, ls=0.6),
         text(P, 74, "Rush Labs →", "sans", 24, t["text"], 700, ls=-0.3)]
    for i, line in enumerate(lines):
        b.append(text(P, 102 + i * 21, line, "sans", 16, t["muted"]))
    return svg(W, H, LAB_ALT, "".join(b), t)


# ── Path: three steps, oldest first ─────────────────────────────────────────
PATH = [("2021", "Product analyst", "Payments software for banks"),
        ("2021–26", "Systems engineer", "Low-latency trading systems, Rust and Go"),
        ("2026–now", "Founder, Rush Labs", "Open-source AI search, NVIDIA Inception")]
PATH_ALT = "Path: " + " ".join(f"{y}, {r}: {d}." for y, r, d in PATH)
PATH_CSS = (".now{animation:now 2.4s ease-out 1s infinite both}"
            "@keyframes now{0%{opacity:.8;transform:scale(1)}100%{opacity:0;transform:scale(3)}}")


def path(t):
    W, H = 1000, 176
    col = (W - 2 * PAD) / 3
    b = [text(PAD, 46, "PATH", "sans", 14, t["accent"], 700, ls=1),
         f'<line x1="{PAD + 6}" y1="74" x2="{PAD + 2 * col + 6:.0f}" y2="74" stroke="{t["border"]}" stroke-width="2"/>']
    for i, (year, role, desc) in enumerate(PATH):
        x = PAD + i * col
        last = i == len(PATH) - 1
        if last:
            b.append(f'<circle class="fx now pivot" cx="{x + 6:.0f}" cy="74" r="6" fill="none" stroke="{t["ok"]}" stroke-width="1.5"/>')
        b.append(f'<circle cx="{x + 6:.0f}" cy="74" r="6" fill="{t["ok"] if last else t["border"]}"/>')
        b.append(text(round(x, 1), 110, year, "mono", 14, t["muted"]))
        b.append(text(round(x, 1), 136, role, "sans", 19, t["text"], 700))
        b.append(text(round(x, 1), 160, desc, "sans", 15, t["muted"]))
    return svg(W, H, PATH_ALT, "".join(b), t, PATH_CSS)


def path_m(t):
    W, P, row = 400, 24, 74
    H = 60 + row * len(PATH)
    b = [text(P, 40, "PATH", "sans", 13, t["accent"], 700, ls=0.6),
         f'<line x1="{P + 6}" y1="66" x2="{P + 6}" y2="{66 + row * (len(PATH) - 1)}" stroke="{t["border"]}" stroke-width="2"/>']
    for i, (year, role, desc) in enumerate(PATH):
        y = 66 + i * row
        last = i == len(PATH) - 1
        b.append(f'<circle cx="{P + 6}" cy="{y}" r="6" fill="{t["ok"] if last else t["border"]}"/>')
        b.append(text(P + 24, y + 5, f"{year} · {role}", "sans", 17, t["text"], 700))
        b.append(text(P + 24, y + 28, desc, "sans", 15, t["muted"]))
    return svg(W, H, PATH_ALT, "".join(b), t, PATH_CSS)


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
    W, H = 400, 438
    css = (".ring{animation:ring 2.4s ease-out 1s infinite both}"
           "@keyframes ring{0%{opacity:.8;transform:scale(1)}100%{opacity:0;transform:scale(3.2)}}")
    P = 24
    b = [text(P, 46, "FOUNDER · RUSH LABS", "sans", 14, t["accent"], 700, ls=0.4),
         text(P - 2, 110, "Vayz", "sans", 62, t["text"], 700, ls=-1),
         text(P, 146, TAGLINE[0], "sans", 19, t["muted"]),
         text(P, 171, TAGLINE[1], "sans", 19, t["muted"]),
         f'<circle class="fx ring pivot" cx="{P + 6}" cy="205" r="5" fill="none" stroke="{t["ok"]}" stroke-width="1.5"/>',
         f'<circle cx="{P + 6}" cy="205" r="5" fill="{t["ok"]}"/>',
         text(P + 20, 211, STATUS, "sans", 17, t["text"], 700),
         f'<line x1="{P}" y1="234" x2="{W - P}" y2="234" stroke="{t["border"]}"/>']
    for i, (v, caps) in enumerate(METRICS):
        x = P + (i % 2) * 180
        y = 278 + (i // 2) * 84
        b.append(text(x, y, v, "sans", 28, t["text"], 700))
        for j, c in enumerate(caps):
            b.append(text(x, y + 22 + j * 19, c, "sans", 15, t["muted"]))
    return svg(W, H, HEADER_ALT, "".join(b), t, css)


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

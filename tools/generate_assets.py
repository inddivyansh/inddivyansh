#!/usr/bin/env python3
"""
Generates the SVG assets used by the profile README.

    python tools/generate_assets.py        # everything except the snake
    python tools/generate_snake.py         # contribution snake (needs network)

Output layout:
  assets/banners/        hero.svg (initial card content, transparent visual style), ending.svg
  assets/headings/       pure typewriter heading SVGs (transparent, NO cards)
  assets/about/          terminal.svg (animated developer terminal)
  assets/status/         availability.svg
  assets/achievements/   achievements.svg
  assets/profiles/       codechef.svg, codeforces.svg (minimal platform UI)
  assets/snake/          snake.svg (from generate_snake.py)

Every file is self-contained SVG with valid XML entities and transparent backgrounds.
Colours adapt to GitHub light / dark mode through `prefers-color-scheme`.
"""
import math
import random
import shutil
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# ----------------------------------------------------------------------------
# CONFIG: accurate live stats
# ----------------------------------------------------------------------------
CODECHEF = dict(
    user="divyanshindian",
    rating=1570,
    stars=2,
    contests=19,
    next_stars=3,
    next_rating=1600,
)
CODEFORCES = dict(
    user="divyansh.indian1",
    rating=1240,
    rank="Pupil",
    contests=9,
    max_rating=1240,
    next_rank="Specialist",
    next_rating=1400,
)

HEADINGS = [
    ("about", "About Me", "blue"),
    ("experience", "Experience", "green"),
    ("projects", "Featured Projects", "orange"),
    ("tech-stack", "Tech Stack", "purple"),
    ("achievements", "Achievements", "pink"),
    ("coding-profiles", "Coding Profiles", "blue"),
    ("github-stats", "GitHub Stats", "green"),
    ("contribution-snake", "Contribution Snake", "orange"),
    ("contact", "Contact", "purple"),
]

QUOTES = [
    ("Talk is cheap. Show me the code.", "Linus Torvalds", "blue"),
    ("First, solve the problem. Then, write the code.", "John Johnson", "green"),
    ("Make it work, make it right, make it fast.", "Kent Beck", "orange"),
    ("Premature optimization is the root of all evil.", "Donald Knuth", "purple"),
    ("Code. Fail. Learn. Repeat.", "my motto", "pink"),
]
CLOSING = "Thanks for stopping by. Happy coding!"

# ----------------------------------------------------------------------------
# typography & colours (light / dark aware, 100% transparent backgrounds)
# ----------------------------------------------------------------------------
MONO = "'Fira Code','JetBrains Mono','SFMono-Regular',Consolas,'Courier New',monospace"
SANS = "'Segoe UI',Inter,-apple-system,'Helvetica Neue',Arial,sans-serif"

ACCENTS = {
    "blue": ("#0969da", "#58a6ff"),
    "green": ("#1a7f37", "#3fb950"),
    "purple": ("#8250df", "#bc8cff"),
    "orange": ("#bc4c00", "#f0883e"),
    "pink": ("#bf3989", "#f778ba"),
    "cyan": ("#0891b2", "#22d3ee"),
}

THEME_CSS = (
    "".join(f".f-{k}{{fill:{v[0]}}}.s-{k}{{stroke:{v[0]}}}" for k, v in ACCENTS.items())
    + ".tx{fill:#1f2328}.mu{fill:#656d76}.ln{stroke:#8b949e;stroke-opacity:.25}"
    + "@media (prefers-color-scheme: dark){"
    + "".join(f".f-{k}{{fill:{v[1]}}}.s-{k}{{stroke:{v[1]}}}" for k, v in ACCENTS.items())
    + ".tx{fill:#e6edf3}.mu{fill:#8b949e}}"
)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print("wrote", path.relative_to(ROOT))


def kt(values) -> str:
    return ";".join(f"{v:.4f}" if v else "0" for v in values)


def type_events(t0, n, dt):
    return [(t0 + i * dt, i + 1) for i in range(n)]


def typed(uid, text, xs, y, fs, cls, T, events, weight=700):
    n = len(text)
    cw = fs * 0.6
    full = n * cw
    times = [0.0] + [e[0] for e in events]
    chars = [0] + [e[1] for e in events]
    keys = kt([t / T for t in times])
    widths = ";".join(f"{c * cw:.1f}" for c in chars)
    xs_cur = ";".join(f"{xs + c * cw:.1f}" for c in chars)
    window = f"0;{events[0][0] / T:.4f};{events[-1][0] / T:.4f}"
    return f"""
    <clipPath id="{uid}"><rect x="{xs:.1f}" y="{y - fs:.1f}" width="0" height="{fs * 1.5:.1f}">
      <animate attributeName="width" calcMode="discrete" values="{widths}" keyTimes="{keys}" dur="{T}s" repeatCount="indefinite"/>
    </rect></clipPath>
    <g clip-path="url(#{uid})"><text x="{xs:.1f}" y="{y}" font-family="{MONO}" font-size="{fs}" font-weight="{weight}" class="{cls}" textLength="{full:.1f}" lengthAdjust="spacing">{escape(text)}</text></g>
    <g opacity="0"><animate attributeName="opacity" calcMode="discrete" values="0;1;0" keyTimes="{window}" dur="{T}s" repeatCount="indefinite"/>
      <rect x="{xs:.1f}" y="{y - fs * 0.95:.1f}" width="{max(2.0, fs * 0.11):.1f}" height="{fs * 1.15:.1f}" class="{cls}">
        <animate attributeName="x" calcMode="discrete" values="{xs_cur}" keyTimes="{keys}" dur="{T}s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>
      </rect></g>"""


# ----------------------------------------------------------------------------
# section headings: pure typewriter SVG, transparent background, NO CARD
# ----------------------------------------------------------------------------
def heading(fname: str, title: str, accent: str) -> None:
    W, H, fs, T = 600, 36, 22, 16
    prefix = "> "
    full_text = f"{prefix}{title}"
    n = len(full_text)
    cw = fs * 0.6
    xs = (W - n * cw) / 2
    ev = type_events(0.4, n, 0.065) + [(T - 0.5, 0)]
    body = typed(f"h-{fname}", full_text, xs, 26, fs, f"f-{accent}", T, ev, weight=700)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(title)}">
  <style>{THEME_CSS}</style>
  {body}
</svg>"""
    write(ASSETS / "headings" / f"{fname}.svg", svg)


# ----------------------------------------------------------------------------
# hero: initial card content (Data Science, ML visualizations, rotating roles),
#       refactored into a sleek transparent visual style (no rectangular card box)
# ----------------------------------------------------------------------------
def hero() -> None:
    W, H = 1200, 310
    r = random.Random(7)

    # subtle matrix code rain (transparent background)
    matrix = []
    for i in range(16):
        x = 30 + i * 75
        rows = "".join(
            f'<tspan x="{x}" dy="16">{r.choice("01")}{r.choice("01")}{r.choice("0123456789")}</tspan>'
            for _ in range(22)
        )
        matrix.append(
            f'<text x="{x}" y="-100" font-family="{MONO}" font-size="12" class="mat">{rows}'
            f'<animateTransform attributeName="transform" type="translate" values="0 0;0 48" dur="{r.randint(9, 18)}s" repeatCount="indefinite"/></text>'
        )

    # right: scatter plot + regression
    px0, px1, py0, py1 = 700, 1020, 52, 245
    grid = "".join(
        f'<line x1="{px0}" y1="{y}" x2="{px1}" y2="{y}" class="gl"/>'
        for y in range(py0 + 38, py1, 38)
    ) + "".join(
        f'<line x1="{x}" y1="{py0}" x2="{x}" y2="{py1}" class="gl"/>'
        for x in range(px0 + 38, px1, 38)
    )
    sx0, sy0 = px0 + 20, py1 - 20
    sx1, sy1 = px1 - 20, py0 + 36
    dots = []
    for _ in range(46):
        t = r.random()
        x = sx0 + t * (sx1 - sx0)
        y = sy0 - t * (sy0 - sy1) + r.gauss(0, 13)
        y = min(py1 - 6, max(py0 + 16, y))
        cls = "dot-c" if abs(y - (sy0 - t * (sy0 - sy1))) < 13 else "dot-p"
        dots.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" class="{cls}">'
            f'<animate attributeName="r" values="2.5;4.5;2.5" dur="{r.uniform(2.4, 4):.1f}s" begin="{r.uniform(0, 3):.1f}s" repeatCount="indefinite"/></circle>'
        )

    # right: histogram
    hx, hb = 1055, 245
    bars = []
    for i in range(10):
        h = round(96 * math.exp(-(((i - 4.5) / 2.6) ** 2)) + 8)
        x = hx + i * 12
        bars.append(
            f'<rect x="{x}" y="{hb}" width="9" height="0" rx="1.5" class="bar">'
            f'<animate attributeName="height" values="0;{h};{h};0" keyTimes="0;0.35;0.9;1" dur="8s" begin="{i * 0.12:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="y" values="{hb};{hb - h};{hb - h};{hb}" keyTimes="0;0.35;0.9;1" dur="8s" begin="{i * 0.12:.2f}s" repeatCount="indefinite"/></rect>'
        )

    # left: rotating neutral roles
    roles = [
        "Final Year CSE @ IIIT Pune",
        "Data Science &amp; Machine Learning",
        "Data Analytics &amp; Quantitative Analysis",
        "Problem Solving &amp; Data Structures in C++",
        "RAG &amp; Generative AI Systems",
    ]
    n = len(roles)
    role_svg = []
    for k, text in enumerate(roles):
        s, e = k / n, (k + 1) / n
        kts = f"0;{s:.4f};{s + 0.015:.4f};{e - 0.015:.4f};{e:.4f};1"
        role_svg.append(
            f'<text x="86" y="202" font-family="{MONO}" font-size="22" class="role" opacity="0">{text}'
            f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{kts}" dur="{n * 3}s" repeatCount="indefinite"/></text>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Divyansh Nagar: AI, Data Science, Backend, Full-Stack, Competitive Programming">
  <defs>
    <linearGradient id="nm" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="100%" stop-color="#818cf8"/>
    </linearGradient>
  </defs>
  <style>
    {THEME_CSS}
    .prompt {{ fill: #64748b; font-family: {MONO}; font-size: 14.5px; }}
    .name {{ font-family: {SANS}; font-size: 64px; font-weight: 800; }}
    .role {{ font-family: {MONO}; font-size: 22px; fill: #38bdf8; }}
    .prompt-arrow {{ font-family: {MONO}; font-size: 22px; fill: #3fb950; }}
    .tagline {{ font-family: {MONO}; font-size: 13.5px; fill: #94a3b8; }}
    .mat {{ fill: #38bdf8; opacity: 0.07; }}
    .gl {{ stroke: #64748b; stroke-opacity: 0.2; stroke-width: 1; }}
    .axis {{ stroke: #64748b; stroke-opacity: 0.45; stroke-width: 1.2; fill: none; }}
    .dot-c {{ fill: #38bdf8; opacity: 0.85; }}
    .dot-p {{ fill: #c084fc; opacity: 0.85; }}
    .reg {{ stroke: #fb923c; stroke-width: 2.2; stroke-linecap: round; fill: none; }}
    .bar {{ fill: #34d399; opacity: 0.85; }}
    .lbl {{ fill: #64748b; font-family: {MONO}; font-size: 11.5px; }}
    .pulse-bar {{ fill: #38bdf8; }}
    @media (prefers-color-scheme: light) {{
      .prompt {{ fill: #64748b; }}
      .role {{ fill: #0284c7; }}
      .prompt-arrow {{ fill: #16a34a; }}
      .tagline {{ fill: #475569; }}
      .mat {{ fill: #0284c7; opacity: 0.05; }}
      .gl {{ stroke: #94a3b8; stroke-opacity: 0.25; }}
      .axis {{ stroke: #64748b; stroke-opacity: 0.5; }}
      .dot-c {{ fill: #0284c7; }}
      .dot-p {{ fill: #9333ea; }}
      .reg {{ stroke: #ea580c; }}
      .bar {{ fill: #059669; }}
      .lbl {{ fill: #475569; }}
      .pulse-bar {{ fill: #0284c7; }}
    }}
  </style>

  {''.join(matrix)}

  <!-- Left: Developer Identity -->
  <text x="50" y="68" class="prompt">&gt;&gt;&gt; import numpy as np, pandas as pd, sklearn</text>
  <text x="48" y="148" class="name" fill="url(#nm)">Divyansh Nagar</text>
  <text x="50" y="202" class="prompt-arrow">&gt;</text>
  {''.join(role_svg)}
  <text x="50" y="248" class="tagline">AI  ·  Data Science  ·  Backend  ·  Full-Stack  ·  Competitive Programming</text>
  <rect x="50" y="266" width="160" height="3" rx="1.5" class="pulse-bar">
    <animate attributeName="width" values="40;240;40" dur="5s" repeatCount="indefinite"/>
  </rect>

  <!-- Right: ML Scatter Plot + Regression Line -->
  <text x="{px0}" y="{py0 - 12}" class="lbl">model.fit(X, y)  →  ŷ = βx + ε</text>
  {grid}
  <path d="M{px0} {py0}V{py1}H{px1}" class="axis"/>
  {''.join(dots)}
  <path d="M{sx0} {sy0}L{sx1} {sy1}" class="reg" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100">
    <animate attributeName="stroke-dashoffset" values="100;0;0;100" keyTimes="0;0.4;0.9;1" dur="8s" repeatCount="indefinite"/>
  </path>

  <!-- Right: Histogram -->
  <text x="{hx}" y="{hb - 120}" class="lbl">hist(residuals)</text>
  <line x1="{hx - 6}" y1="{hb + 1}" x2="{hx + 124}" y2="{hb + 1}" class="axis"/>
  {''.join(bars)}
</svg>"""
    write(ASSETS / "banners" / "hero.svg", svg)


# ----------------------------------------------------------------------------
# About Me: animated developer terminal (authentic macOS / Linux terminal)
# ----------------------------------------------------------------------------
def terminal() -> None:
    W = 860
    LH, y0 = 23, 76
    G, FG, MU, BL = "#3fb950", "#e6edf3", "#8b949e", "#58a6ff"
    script = [
        ("cmd", "whoami"),
        ("out", [("Divyansh Nagar", FG), ("  /  B.Tech CSE, IIIT Pune (2023 - 2027)", MU)]),
        ("cmd", "cat about.txt"),
        ("out", [("I turn machine learning and backend engineering into products:", FG)]),
        ("out", [("RAG document intelligence, real-time AI security, satellite data.", FG)]),
        ("out", [("300+ DSA problems solved, mostly in ", FG), ("C++", BL), (".", FG)]),
        ("cmd", "ls focus/"),
        ("out", [("generative-ai/  ", BL), ("backend-apis/  ", BL), ("ml-time-series/  ", BL), ("ai-security/", BL)]),
        ("cmd", "echo $STATUS"),
        ("out", [("open to ", FG), ("internships", G), (" and ", FG), ("full-time opportunities", G)]),
        ("idle",),
    ]
    H = y0 + len(script) * LH + 14
    fs = 14
    cw = fs * 0.6
    T = 30.0
    t = 0.8
    rows, defs = [], []
    for i, item in enumerate(script):
        y = y0 + i * LH
        if item[0] == "cmd":
            cmd = item[1]
            n = len(cmd)
            px = 28 + 2 * cw
            ev = type_events(t, n, 0.09)
            keys = kt([0] + [e[0] / T for e in ev])
            counts = [0] + [c for _, c in ev]
            widths = ";".join(f"{c * cw:.1f}" for c in counts)
            xs = ";".join(f"{px + c * cw:.1f}" for c in counts)
            nxt = ev[-1][0] + 0.55
            defs.append(
                f'<clipPath id="c{i}"><rect x="{px:.1f}" y="{y - fs}" width="0" height="{fs * 1.5:.1f}">'
                f'<animate attributeName="width" calcMode="discrete" values="{widths}" keyTimes="{keys}" dur="{T}s" repeatCount="indefinite"/></rect></clipPath>'
            )
            rows.append(
                f'<text x="28" y="{y}" font-family="{MONO}" font-size="{fs}" fill="{G}" font-weight="700" opacity="0">$'
                f'<animate attributeName="opacity" calcMode="discrete" values="0;1" keyTimes="0;{(t - 0.05) / T:.4f}" dur="{T}s" repeatCount="indefinite"/></text>'
                f'<g clip-path="url(#c{i})"><text x="{px:.1f}" y="{y}" font-family="{MONO}" font-size="{fs}" fill="{FG}" textLength="{n * cw:.1f}" lengthAdjust="spacing">{escape(cmd)}</text></g>'
                f'<g opacity="0"><animate attributeName="opacity" calcMode="discrete" values="0;1;0" keyTimes="0;{t / T:.4f};{nxt / T:.4f}" dur="{T}s" repeatCount="indefinite"/>'
                f'<rect x="{px:.1f}" y="{y - 12}" width="8" height="16" fill="{FG}" opacity="0.85">'
                f'<animate attributeName="x" calcMode="discrete" values="{xs}" keyTimes="{keys}" dur="{T}s" repeatCount="indefinite"/></rect></g>'
            )
            t = nxt
        elif item[0] == "out":
            spans = "".join(f'<tspan fill="{c}">{escape(s)}</tspan>' for s, c in item[1])
            rows.append(
                f'<text x="28" y="{y}" font-family="{MONO}" font-size="{fs}" opacity="0" xml:space="preserve">{spans}'
                f'<animate attributeName="opacity" calcMode="discrete" values="0;1" keyTimes="0;{t / T:.4f}" dur="{T}s" repeatCount="indefinite"/></text>'
            )
            t += 0.55
        else:
            rows.append(
                f'<g opacity="0"><animate attributeName="opacity" calcMode="discrete" values="0;1" keyTimes="0;{t / T:.4f}" dur="{T}s" repeatCount="indefinite"/>'
                f'<text x="28" y="{y}" font-family="{MONO}" font-size="{fs}" fill="{G}" font-weight="700">$</text>'
                f'<rect x="{28 + 2 * cw:.1f}" y="{y - 12}" width="8" height="16" fill="{FG}" opacity="0.85"><animate attributeName="opacity" values="0.85;0;0.85" dur="1s" repeatCount="indefinite"/></rect></g>'
            )
            t += 3
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Terminal: whoami, about, focus areas and availability">
  <defs>{''.join(defs)}</defs>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="8" fill="#0d1117" stroke="#30363d"/>
  <path d="M0.5 36H{W - 0.5}" stroke="#30363d"/>
  <circle cx="22" cy="19" r="5.5" fill="#ff5f56"/><circle cx="42" cy="19" r="5.5" fill="#ffbd2e"/><circle cx="62" cy="19" r="5.5" fill="#27c93f"/>
  <text x="{W / 2}" y="23" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{MU}">divyansh@iiit-pune: ~</text>
  {''.join(rows)}
</svg>"""
    write(ASSETS / "about" / "terminal.svg", svg)


# ----------------------------------------------------------------------------
# availability: transparent pulsing live status
# ----------------------------------------------------------------------------
def availability() -> None:
    W, H = 900, 32
    msg = "Open to internships and full-time opportunities"
    fs = 14
    tw = len(msg) * fs * 0.6
    x = (W - tw - 26) / 2
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{msg}">
  <style>{THEME_CSS}</style>
  <circle cx="{x + 6:.1f}" cy="16" r="4.5" class="f-green"/>
  <circle cx="{x + 6:.1f}" cy="16" r="4.5" class="s-green" fill="none" stroke-width="1.5">
    <animate attributeName="r" values="4.5;11" dur="1.8s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.8;0" dur="1.8s" repeatCount="indefinite"/>
  </circle>
  <text x="{x + 22:.1f}" y="21" font-family="{MONO}" font-size="{fs}" font-weight="600" class="f-green" textLength="{tw:.1f}" lengthAdjust="spacing">{msg}</text>
</svg>"""
    write(ASSETS / "status" / "availability.svg", svg)


# ----------------------------------------------------------------------------
# achievements: transparent typographic grid, NO cards, minimal spacing
# ----------------------------------------------------------------------------
def achievements() -> None:
    items = [
        ("AIR 43", "green", "Naukri EROH 2025", "Round 2, 6,000+ candidates", "AI in Renewable Energy"),
        ("Top 10%", "blue", "ISRO BAH 2025", "500+ teams nationwide", "Aditya-L1 Halo CME detection"),
        ("CS50x", "purple", "Harvard University", "Intro to Computer Science", "C, Python, SQL, Memory, Algos"),
        ("Rank 1621", "orange", "CodeChef Starters 225", "Global competitive rank", "Rated 2★ (1570 peak)"),
        ("97.81 %ile", "pink", "JEE Main 2023", "~1 Million candidates", "Top tier national engineering rank"),
        ("300+", "cyan", "DSA Problems Solved", "Practiced mainly in C++", "LeetCode, CodeChef, Codeforces"),
    ]
    W, colw, rowh = 900, 300, 88
    H = rowh * 2 + 10
    out = []
    for i, (m, acc, title, l1, l2) in enumerate(items):
        x = (i % 3) * colw + 24
        y = (i // 3) * rowh
        out.append(
            f'<text x="{x}" y="{y + 28}" font-family="{SANS}" font-size="26" font-weight="800" class="f-{acc}">{escape(m)}</text>'
            f'<text x="{x}" y="{y + 48}" font-family="{SANS}" font-size="14" font-weight="700" class="tx">{escape(title)}</text>'
            f'<text x="{x}" y="{y + 66}" font-family="{SANS}" font-size="11.5" class="mu">{escape(l1)}</text>'
            f'<text x="{x}" y="{y + 80}" font-family="{SANS}" font-size="11.5" class="mu">{escape(l2)}</text>'
        )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Achievements: AIR 43 Naukri EROH, ISRO BAH top 10 percent, Harvard CS50x, CodeChef rank 1621, JEE Main 97.81 percentile, 300+ DSA problems">
  <style>{THEME_CSS}</style>
  {''.join(out)}
</svg>"""
    write(ASSETS / "achievements" / "achievements.svg", svg)


# ----------------------------------------------------------------------------
# CodeChef: Profile card matching LeetCode dark theme (500x150)
# ----------------------------------------------------------------------------
def codechef() -> None:
    c = CODECHEF
    W, H = 500, 150
    stars = f"{c['stars']}\u2605"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="CodeChef {c['user']}: rating {c['rating']}, {stars}">
  <style>
    .bg {{ fill: #101010; }}
    .border {{ stroke: #333333; }}
    .rank {{ fill: #ffa116; font-family: {SANS}; font-size: 14px; font-weight: 700; }}
    .username {{ fill: #ffa116; font-family: {SANS}; font-size: 24px; font-weight: 800; }}
    .lbl {{ fill: #8b949e; font-family: {SANS}; font-size: 13px; }}
    .val {{ fill: #e6edf3; font-family: {SANS}; font-size: 13px; font-weight: 700; }}
    .hi {{ fill: #ffa116; font-family: {SANS}; font-size: 13px; font-weight: 700; }}
    .max-lbl {{ fill: #6e7681; font-family: {SANS}; font-size: 12px; }}
    .plt {{ fill: #8b949e; font-family: {MONO}; font-size: 11px; font-weight: 700; letter-spacing: 2px; }}
    .dv {{ stroke: #262626; }}
  </style>
  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="8" class="bg"/>
  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="8" fill="none" stroke-width="1" class="border"/>
  <rect x="22" y="19" width="4" height="12" rx="1" fill="#ffa116"/>
  <rect x="29" y="16" width="4" height="15" rx="1" fill="#ffa116" opacity="0.8"/>
  <rect x="36" y="21" width="4" height="10" rx="1" fill="#ffa116" opacity="0.6"/>
  <text x="48" y="29" class="plt">CODECHEF</text>
  <text x="22" y="58" class="rank">{stars}</text>
  <text x="22" y="86" class="username">{escape(c['user'])}</text>
  <line x1="22" y1="102" x2="{W-22}" y2="102" class="dv" stroke-width="1"/>
  <text x="22" y="125" class="lbl">Contest rating: </text>
  <text x="116" y="125" class="hi">{c['rating']}</text>
  <text x="152" y="125" class="max-lbl"> (max. {stars}, {c['rating']})</text>
  <text x="{W-22}" y="125" text-anchor="end" class="lbl">Contests: <tspan class="val">{c['contests']}</tspan></text>
</svg>"""
    write(ASSETS / "profiles" / "codechef.svg", svg)


# ----------------------------------------------------------------------------
# Codeforces: Profile card matching LeetCode dark theme (500x150)
# ----------------------------------------------------------------------------
def codeforces() -> None:
    c = CODEFORCES
    W, H = 500, 150

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Codeforces {c['user']}: {c['rank']}, rating {c['rating']}">
  <style>
    .bg {{ fill: #101010; }}
    .border {{ stroke: #333333; }}
    .rank {{ fill: #77bb41; font-family: {SANS}; font-size: 14px; font-weight: 700; }}
    .username {{ fill: #77bb41; font-family: {SANS}; font-size: 24px; font-weight: 800; }}
    .lbl {{ fill: #8b949e; font-family: {SANS}; font-size: 13px; }}
    .val {{ fill: #e6edf3; font-family: {SANS}; font-size: 13px; font-weight: 700; }}
    .hi {{ fill: #77bb41; font-family: {SANS}; font-size: 13px; font-weight: 700; }}
    .max-lbl {{ fill: #6e7681; font-family: {SANS}; font-size: 12px; }}
    .plt {{ fill: #8b949e; font-family: {MONO}; font-size: 11px; font-weight: 700; letter-spacing: 2px; }}
    .dv {{ stroke: #262626; }}
  </style>
  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="8" class="bg"/>
  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="8" fill="none" stroke-width="1" class="border"/>
  <rect x="22" y="21" width="4" height="10" rx="1" fill="#F3B431"/>
  <rect x="29" y="16" width="4" height="15" rx="1" fill="#3065c0"/>
  <rect x="36" y="18" width="4" height="13" rx="1" fill="#C0392B"/>
  <text x="48" y="29" class="plt">CODEFORCES</text>
  <text x="22" y="58" class="rank">{escape(c['rank'])}</text>
  <text x="22" y="86" class="username">{escape(c['user'])}</text>
  <line x1="22" y1="102" x2="{W-22}" y2="102" class="dv" stroke-width="1"/>
  <text x="22" y="125" class="lbl">Contest rating: </text>
  <text x="116" y="125" class="hi">{c['rating']}</text>
  <text x="152" y="125" class="max-lbl"> (max. {escape(c['rank'].lower())}, {c['max_rating']})</text>
  <text x="{W-22}" y="125" text-anchor="end" class="lbl">Contests: <tspan class="val">{c['contests']}</tspan></text>
</svg>"""
    write(ASSETS / "profiles" / "codeforces.svg", svg)


# ----------------------------------------------------------------------------
# ending: quotes typed one after another, transparent background, NO CARD
# ----------------------------------------------------------------------------
def ending() -> None:
    W, H = 900, 80
    slot = 7.0
    items = [(q, a, c) for q, a, c in QUOTES] + [(CLOSING, None, "blue")]
    T = slot * len(items)
    parts = []
    for i, (text, author, accent) in enumerate(items):
        shown = f"\u201c{text}\u201d" if author else text
        n, fs = len(shown), 18
        xs = (W - n * fs * 0.6) / 2
        t0 = i * slot + 0.3
        ev = type_events(t0, n, 0.04)
        hold_end = ev[-1][0] + 3.0
        ev += [(hold_end + j * 0.012, n - 1 - j) for j in range(n)]
        parts.append(typed(f"q{i}", shown, xs, 36, fs, f"f-{accent}", T, ev))
        if author:
            a0 = ev[n - 1][0] + 0.2
            a1 = hold_end
            parts.append(
                f'<text x="{W / 2}" y="58" text-anchor="middle" font-family="{MONO}" font-size="12.5" class="mu" opacity="0">'
                f'\u2014 {escape(author)}'
                f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{a0 / T:.4f};{(a0 + 0.4) / T:.4f};{a1 / T:.4f};{(a1 + 0.3) / T:.4f};1" dur="{T}s" repeatCount="indefinite"/></text>'
            )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Closing quotes">
  <style>{THEME_CSS}</style>
  {''.join(parts)}
</svg>"""
    write(ASSETS / "banners" / "ending.svg", svg)


def main() -> None:
    for sub in ("banners", "headings", "profiles", "highlights", "about", "status", "achievements"):
        shutil.rmtree(ASSETS / sub, ignore_errors=True)
    hero()
    terminal()
    ending()
    for f, t, a in HEADINGS:
        heading(f, t, a)
    availability()
    achievements()
    codechef()
    codeforces()


if __name__ == "__main__":
    main()

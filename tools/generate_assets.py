#!/usr/bin/env python3
"""
Generates every animated SVG used by the profile README.

Run from the repo root:   python tools/generate_assets.py

Output layout
  assets/banners/     hero.svg, footer.svg
  assets/headings/    one animated "notebook cell" heading per section
  assets/profiles/    coding-platform stat cards   (edit CONFIG below, re-run)
  assets/highlights/  achievement cards            (edit CONFIG below, re-run)

No external services or fonts are needed: every file is self-contained SVG
(SMIL animation), so GitHub renders it through a plain <img> tag.
"""
import math
import random
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

MONO = "'Fira Code','JetBrains Mono','SFMono-Regular',Consolas,'Courier New',monospace"
SANS = "'Segoe UI',Inter,'Helvetica Neue',Arial,sans-serif"

CYAN, GREEN, PURPLE, ORANGE, PINK = "#38bdf8", "#34d399", "#a78bfa", "#fb923c", "#f472b6"
BG1, BG2, BG3 = "#0f2027", "#203a43", "#2c5364"   # same palette as the first README

# ----------------------------------------------------------------------------
# CONFIG: edit numbers here after contests, then re-run the script
# ----------------------------------------------------------------------------
HEADINGS = [
    # file,              title,               accent
    ("coding-profiles",  "Coding Profiles",   CYAN),
    ("highlights",       "Highlights",        GREEN),
    ("about",            "About Me",          PURPLE),
    ("projects",         "Featured Projects", ORANGE),
    ("tech-stack",       "Tech Stack",        CYAN),
    ("experience",       "Experience",        GREEN),
    ("github-stats",     "GitHub Stats",      PURPLE),
    ("contribution-snake", "Contribution Snake", ORANGE),
    ("contact",          "Contact",           PINK),
]

PROFILE_CARDS = [
    # file, label, big, sub, caption lines, accent, bar fraction (0-1) or None
    ("codechef",   "CODECHEF",   "1570", "2 Star  ·  divyanshindian",
     ["Global Rank 1621", "Starters 225"], "#e0a878", 1570 / 3000),
    ("codeforces", "CODEFORCES", "1240", "Pupil  ·  divyansh.indian1",
     ["Competitive programming"], "#4aa8e8", 1240 / 3000),
    ("leetcode",   "LEETCODE",   "1573", "Top 28%  ·  inddivyansh",
     ["Contest rating"], "#ffb02e", 0.72),
    ("dsa",        "DSA",        "300+", "Problems solved",
     ["Sharpening in C++"], GREEN, None),
]

HIGHLIGHT_CARDS = [
    ("air-43",     "NAUKRI EROH 2025", "AIR 43", "Round 2  ·  6000+ participants",
     ["AI in Renewable Energy"], GREEN, 0.993),
    ("isro-bah",   "ISRO BAH 2025", "Top 10%", "500+ teams",
     ["Aditya-L1 telemetry"], CYAN, 0.90),
    ("jee-main",   "JEE MAIN 2023", "97.81 %ile", "1 million candidates",
     ["National engineering entrance"], PURPLE, 0.9781),
    ("army-intern", "AUG - OCT 2026", "Army Intern", "Information Warfare",
     ["Indian Army Southern Command"], ORANGE, None),
]


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print("wrote", path.relative_to(ROOT))


def bg_defs(prefix: str = "") -> str:
    return f"""
    <linearGradient id="{prefix}bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{BG1}"/><stop offset="0.55" stop-color="{BG2}"/><stop offset="1" stop-color="{BG3}"/>
    </linearGradient>
    <pattern id="{prefix}grid" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M20 0H0V20" fill="none" stroke="#ffffff" stroke-opacity="0.05"/>
    </pattern>"""


# ----------------------------------------------------------------------------
# section headings: Jupyter-cell style  "In [n]:  Title▌" with a live sparkline
# ----------------------------------------------------------------------------
def heading(idx: int, fname: str, title: str, accent: str) -> None:
    W, H = 900, 64
    r = random.Random(idx * 31 + 5)
    tx = 100
    tw = round(len(title) * 15.2)
    dur = 9
    kt = "0;0.3;0.9;1"

    # sparkline (random walk trending upward)
    x0, x1, y_top, y_bot = 610, 880, 14, 48
    n = 14
    pts, v = [], 0.25
    for i in range(n):
        v = min(0.95, max(0.05, v + r.uniform(-0.12, 0.2)))
        pts.append((x0 + (x1 - x0) * i / (n - 1), y_bot - v * (y_bot - y_top)))
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    area = d + f" L{x1} {y_bot} L{x0} {y_bot} Z"
    ex, ey = pts[-1]

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(title)}">
  <defs>{bg_defs()}
    <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{accent}" stop-opacity="0.35"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{accent}" stop-opacity="0"/><stop offset="0.5" stop-color="{accent}"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="type"><rect x="{tx}" y="0" height="{H}" width="0">
      <animate attributeName="width" values="0;{tw};{tw};0" keyTimes="{kt}" dur="{dur}s" repeatCount="indefinite"/>
    </rect></clipPath>
  </defs>
  <rect width="{W}" height="{H}" rx="10" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" rx="10" fill="url(#grid)"/>
  <rect x="0" y="0" width="5" height="{H}" rx="2" fill="{accent}"/>
  <text x="22" y="38" font-family="{MONO}" font-size="14" fill="#7d8fa3">In [{idx}]:</text>
  <g clip-path="url(#type)">
    <text x="{tx}" y="42" font-family="{MONO}" font-size="25" font-weight="700" fill="#ffffff">{escape(title)}</text>
  </g>
  <rect x="{tx}" y="16" width="2.5" height="32" fill="{accent}">
    <animate attributeName="x" values="{tx};{tx + tw};{tx + tw};{tx}" keyTimes="{kt}" dur="{dur}s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="1;0;1" dur="0.9s" repeatCount="indefinite"/>
  </rect>
  <path d="{area}" fill="url(#fade)" opacity="0.8"/>
  <path d="{d}" fill="none" stroke="{accent}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100">
    <animate attributeName="stroke-dashoffset" values="100;0;0;100" keyTimes="{kt}" dur="{dur}s" repeatCount="indefinite"/>
  </path>
  <circle cx="{ex:.1f}" cy="{ey:.1f}" r="3.5" fill="{accent}">
    <animate attributeName="r" values="3;6;3" dur="1.6s" repeatCount="indefinite"/>
  </circle>
  <rect x="10" y="{H - 4}" width="{W - 20}" height="2" rx="1" fill="#ffffff" opacity="0.06"/>
  <rect x="-160" y="{H - 4}" width="160" height="2" rx="1" fill="url(#sweep)">
    <animate attributeName="x" values="-160;{W}" dur="4s" repeatCount="indefinite"/>
  </rect>
</svg>"""
    write(ASSETS / "headings" / f"{fname}.svg", svg)


# ----------------------------------------------------------------------------
# hero banner: scatter + regression line + histogram + falling binary
# ----------------------------------------------------------------------------
def hero() -> None:
    W, H = 1200, 320
    r = random.Random(7)

    matrix = []
    for i in range(16):
        x = 30 + i * 75
        rows = "".join(
            f'<tspan x="{x}" dy="16">{r.choice("01")}{r.choice("01")}{r.choice("0123456789")}</tspan>'
            for _ in range(26)
        )
        matrix.append(
            f'<text x="{x}" y="-120" font-family="{MONO}" font-size="12" fill="{CYAN}" opacity="0.08">{rows}'
            f'<animateTransform attributeName="transform" type="translate" values="0 0;0 48" dur="{r.randint(9, 18)}s" repeatCount="indefinite"/></text>'
        )

    # scatter plot
    px0, px1, py0, py1 = 690, 1010, 56, 254
    grid = "".join(
        f'<line x1="{px0}" y1="{y}" x2="{px1}" y2="{y}" stroke="#fff" stroke-opacity="0.06"/>'
        for y in range(py0 + 40, py1, 40)
    ) + "".join(
        f'<line x1="{x}" y1="{py0}" x2="{x}" y2="{py1}" stroke="#fff" stroke-opacity="0.06"/>'
        for x in range(px0 + 40, px1, 40)
    )
    sx0, sy0 = px0 + 22, py1 - 22
    sx1, sy1 = px1 - 22, py0 + 40
    dots = []
    for _ in range(46):
        t = r.random()
        x = sx0 + t * (sx1 - sx0)
        y = sy0 - t * (sy0 - sy1) + r.gauss(0, 14)
        y = min(py1 - 6, max(py0 + 18, y))
        col = CYAN if abs(y - (sy0 - t * (sy0 - sy1))) < 14 else PURPLE
        dots.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{col}" opacity="0.9">'
            f'<animate attributeName="r" values="2.5;4.5;2.5" dur="{r.uniform(2.4, 4):.1f}s" begin="{r.uniform(0, 3):.1f}s" repeatCount="indefinite"/></circle>'
        )

    # histogram
    hx, hb = 1045, 254
    bars = []
    for i in range(10):
        h = round(104 * math.exp(-(((i - 4.5) / 2.6) ** 2)) + 8)
        x = hx + i * 12
        bars.append(
            f'<rect x="{x}" y="{hb}" width="9" height="0" rx="1.5" fill="{GREEN}" opacity="0.85">'
            f'<animate attributeName="height" values="0;{h};{h};0" keyTimes="0;0.35;0.9;1" dur="8s" begin="{i * 0.12:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="y" values="{hb};{hb - h};{hb - h};{hb}" keyTimes="0;0.35;0.9;1" dur="8s" begin="{i * 0.12:.2f}s" repeatCount="indefinite"/></rect>'
        )

    roles = [
        "Final Year CSE @ IIIT Pune",
        "Building RAG & AI Security systems",
        "ML on Satellite Time-Series Data",
        "Backend Engineering with FastAPI",
        "300+ DSA problems solved",
    ]
    n = len(roles)
    role_svg = []
    for k, text in enumerate(roles):
        s, e = k / n, (k + 1) / n
        kts = f"0;{s:.4f};{s + 0.015:.4f};{e - 0.015:.4f};{e:.4f};1"
        role_svg.append(
            f'<text x="86" y="214" font-family="{MONO}" font-size="23" fill="{CYAN}" opacity="0">{escape(text)}'
            f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{kts}" dur="{n * 3}s" repeatCount="indefinite"/></text>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Divyansh Nagar: AI, Data Science, Backend, Full-Stack, Competitive Programming">
  <defs>{bg_defs()}
    <linearGradient id="nm" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="{CYAN}"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.8" cy="0.4" r="0.6">
      <stop offset="0" stop-color="{CYAN}" stop-opacity="0.18"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/>
    </radialGradient>
    <clipPath id="round"><rect width="{W}" height="{H}" rx="16"/></clipPath>
  </defs>
  <g clip-path="url(#round)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    <rect width="{W}" height="{H}" fill="url(#glow)"/>
    <rect width="{W}" height="{H}" fill="url(#grid)"/>
    {''.join(matrix)}

    <!-- left: identity -->
    <text x="60" y="78" font-family="{MONO}" font-size="15" fill="#7d8fa3">&gt;&gt;&gt; import numpy as np, pandas as pd, sklearn</text>
    <text x="58" y="160" font-family="{SANS}" font-size="68" font-weight="800" fill="url(#nm)">Divyansh Nagar</text>
    <text x="60" y="214" font-family="{MONO}" font-size="23" fill="{GREEN}">&gt;</text>
    {''.join(role_svg)}
    <text x="60" y="262" font-family="{MONO}" font-size="14" fill="#9fb3c8">AI  ·  Data Science  ·  Backend  ·  Full-Stack  ·  Competitive Programming</text>
    <rect x="60" y="282" width="160" height="3" rx="1.5" fill="{CYAN}">
      <animate attributeName="width" values="40;240;40" dur="5s" repeatCount="indefinite"/>
    </rect>

    <!-- right: scatter + regression -->
    <text x="{px0}" y="{py0 - 14}" font-family="{MONO}" font-size="12" fill="#7d8fa3">model.fit(X, y)  →  ŷ = βx + ε</text>
    {grid}
    <path d="M{px0} {py0}V{py1}H{px1}" fill="none" stroke="#9fb3c8" stroke-opacity="0.5" stroke-width="1.2"/>
    {''.join(dots)}
    <path d="M{sx0} {sy0}L{sx1} {sy1}" stroke="{ORANGE}" stroke-width="2.4" stroke-linecap="round" fill="none" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100">
      <animate attributeName="stroke-dashoffset" values="100;0;0;100" keyTimes="0;0.4;0.9;1" dur="8s" repeatCount="indefinite"/>
    </path>

    <!-- histogram -->
    <text x="{hx}" y="{hb - 128}" font-family="{MONO}" font-size="12" fill="#7d8fa3">hist(residuals)</text>
    <line x1="{hx - 6}" y1="{hb + 1}" x2="{hx + 126}" y2="{hb + 1}" stroke="#9fb3c8" stroke-opacity="0.5"/>
    {''.join(bars)}
  </g>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="none" stroke="#ffffff" stroke-opacity="0.08"/>
</svg>"""
    write(ASSETS / "banners" / "hero.svg", svg)


# ----------------------------------------------------------------------------
# footer banner: converging loss curve
# ----------------------------------------------------------------------------
def footer() -> None:
    W, H = 1200, 150
    r = random.Random(11)
    pts = []
    steps = 70
    for i in range(steps + 1):
        t = i / steps
        x = 40 + t * (W - 80)
        y = 132 - 96 * math.exp(-5 * t) + r.gauss(0, 3.2) * math.exp(-3 * t)
        pts.append((x, y))
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Code. Fail. Learn. Repeat.">
  <defs>{bg_defs()}
    <clipPath id="round"><rect width="{W}" height="{H}" rx="16"/></clipPath>
  </defs>
  <g clip-path="url(#round)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    <rect width="{W}" height="{H}" fill="url(#grid)"/>
    <path id="loss" d="{d}" fill="none" stroke="{CYAN}" stroke-width="2.2" stroke-linejoin="round" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100" opacity="0.75">
      <animate attributeName="stroke-dashoffset" values="100;0;0;100" keyTimes="0;0.6;0.92;1" dur="9s" repeatCount="indefinite"/>
    </path>
    <circle r="5" fill="{ORANGE}">
      <animateMotion dur="5.4s" repeatCount="indefinite" keyPoints="0;1;1" keyTimes="0;0.9;1" calcMode="linear"><mpath href="#loss"/></animateMotion>
    </circle>
    <text x="{W // 2}" y="62" text-anchor="middle" font-family="{MONO}" font-size="28" font-weight="700" fill="#ffffff">Code. Fail. Learn. Repeat.</text>
    <text x="{W // 2}" y="90" text-anchor="middle" font-family="{MONO}" font-size="15" fill="#9fb3c8">loss → 0   ·   epochs → ∞   ·   thanks for stopping by</text>
    <text x="40" y="22" font-family="{MONO}" font-size="11" fill="#7d8fa3">training_loss</text>
    <text x="{W - 40}" y="{H - 8}" text-anchor="end" font-family="{MONO}" font-size="11" fill="#7d8fa3">epoch</text>
  </g>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="none" stroke="#ffffff" stroke-opacity="0.08"/>
</svg>"""
    write(ASSETS / "banners" / "footer.svg", svg)


# ----------------------------------------------------------------------------
# stat cards (profiles + highlights share one design)
# ----------------------------------------------------------------------------
def card(folder: str, fname: str, label: str, big: str, sub: str,
         caption: list, accent: str, bar) -> None:
    W, H = 300, 170
    big_size = 40 if len(big) <= 6 else (32 if len(big) <= 9 else 27)
    cap = "".join(
        f'<text x="22" y="{128 + i * 15}" font-family="{SANS}" font-size="12" fill="#8ea3b8">{escape(c)}</text>'
        for i, c in enumerate(caption)
    )
    bar_svg = ""
    if bar is not None:
        bw = round(256 * bar, 1)
        bar_svg = f"""
  <rect x="22" y="152" width="256" height="6" rx="3" fill="#ffffff" opacity="0.1"/>
  <rect x="22" y="152" width="0" height="6" rx="3" fill="{accent}">
    <animate attributeName="width" values="0;{bw};{bw};0" keyTimes="0;0.3;0.9;1" dur="8s" repeatCount="indefinite"/>
  </rect>"""
    else:  # pulsing dots instead of a bar
        bar_svg = "".join(
            f'<circle cx="{26 + i * 14}" cy="155" r="3" fill="{accent}"><animate attributeName="opacity" values="0.2;1;0.2" dur="1.8s" begin="{i * 0.25}s" repeatCount="indefinite"/></circle>'
            for i in range(8)
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(label)} {escape(big)}">
  <defs>{bg_defs()}
    <radialGradient id="corner" cx="1" cy="0" r="0.9">
      <stop offset="0" stop-color="{accent}" stop-opacity="0.3"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/>
    </radialGradient>
    <clipPath id="round"><rect width="{W}" height="{H}" rx="14"/></clipPath>
  </defs>
  <g clip-path="url(#round)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    <rect width="{W}" height="{H}" fill="url(#grid)"/>
    <rect width="{W}" height="{H}" fill="url(#corner)"/>
    <rect x="-3" y="0" width="2" height="{H}" fill="{accent}" opacity="0.18">
      <animate attributeName="x" values="-3;{W}" dur="6s" repeatCount="indefinite"/>
    </rect>
  </g>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="none" stroke="{accent}" stroke-opacity="0.35"/>
  <circle cx="26" cy="30" r="4" fill="{accent}"><animate attributeName="opacity" values="1;0.25;1" dur="1.8s" repeatCount="indefinite"/></circle>
  <text x="38" y="34" font-family="{MONO}" font-size="12" letter-spacing="1.5" fill="{accent}">{escape(label)}</text>
  <text x="22" y="82" font-family="{SANS}" font-size="{big_size}" font-weight="800" fill="#ffffff">{escape(big)}</text>
  <text x="22" y="106" font-family="{SANS}" font-size="13.5" font-weight="600" fill="#d6e2ee">{escape(sub)}</text>
  {cap}{bar_svg}
</svg>"""
    write(ASSETS / folder / f"{fname}.svg", svg)


def main() -> None:
    hero()
    footer()
    for i, (f, t, a) in enumerate(HEADINGS, start=1):
        heading(i, f, t, a)
    for f, label, big, sub, cap, acc, bar in PROFILE_CARDS:
        card("profiles", f, label, big, sub, cap, acc, bar)
    for f, label, big, sub, cap, acc, bar in HIGHLIGHT_CARDS:
        card("highlights", f, label, big, sub, cap, acc, bar)


if __name__ == "__main__":
    main()

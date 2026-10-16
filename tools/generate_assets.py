#!/usr/bin/env python3
"""
Generates the SVG assets used by the profile README.

    python tools/generate_assets.py        # everything except the snake
    python tools/generate_snake.py         # contribution snake (needs network)

Output layout:
  assets/banners/        hero.svg (floating stickers + typewriter), ending.svg
  assets/headings/       pure typewriter heading SVGs (transparent, NO cards)
  assets/status/         availability.svg
  assets/achievements/   achievements.svg
  assets/profiles/       codechef.svg, codeforces.svg (native platform UI)
  assets/snake/          snake.svg (from generate_snake.py)

Every file is self-contained SVG with transparent backgrounds.
Colours adapt to GitHub light / dark mode through `prefers-color-scheme`.
"""
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
    contests_needed="~1-2",
)
CODEFORCES = dict(
    user="divyansh.indian1",
    rating=1240,
    rank="Pupil",
    contests=9,
    max_rating=1240,
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

HERO_ROLES = [
    "B.Tech CSE @ IIIT Pune '27",
    "AI / ML Engineer: RAG & Generative AI",
    "Backend Developer: FastAPI & PostgreSQL",
    "Competitive Programmer in C++",
    "Open to Internships & Full-Time Roles",
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
# hero: transparent floating stickers / PNG-style composition + typewriter
# ----------------------------------------------------------------------------
def hero() -> None:
    W, H = 900, 155
    slot = 5.2
    T = slot * len(HERO_ROLES)
    name = "Divyansh Nagar"
    fs_name = 44

    parts = []
    for i, role in enumerate(HERO_ROLES):
        display_role = f"❯ {role}"
        n, fs = len(display_role), 18
        xs = (W - n * fs * 0.6) / 2
        t0 = i * slot + 0.3
        ev = type_events(t0, n, 0.04)
        hold_end = ev[-1][0] + 2.0
        ev += [(hold_end + j * 0.018, n - 1 - j) for j in range(n)]
        parts.append(typed(f"hr{i}", display_role, xs, 118, fs, "f-cyan", T, ev, weight=600))

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Divyansh Nagar - AI, Backend & Competitive Programming">
  <defs>
    <linearGradient id="name-grad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="50%" stop-color="#818cf8"/>
      <stop offset="100%" stop-color="#c084fc"/>
    </linearGradient>
    <filter id="sticker-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.25"/>
    </filter>
  </defs>
  <style>
    {THEME_CSS}
    .sticker {{ transition: transform 0.3s ease; }}
  </style>

  <!-- Left Floating Stickers (PNG-style transparent icons) -->
  <!-- Python Sticker -->
  <g class="sticker" filter="url(#sticker-glow)">
    <animateTransform attributeName="transform" type="translate" values="0,0; 0,-6; 0,0" dur="4.2s" repeatCount="indefinite"/>
    <rect x="36" y="22" width="46" height="46" rx="12" fill="#1e293b" fill-opacity="0.75" stroke="#38bdf8" stroke-width="1.2" stroke-opacity="0.6"/>
    <path d="M59 31c-5.5 0-5.2 2.4-5.2 2.4l.01 2.5h5.3v.7H51.7s-3.5-.4-3.5 5.2 3.1 5.1 3.1 5.1h1.8v-2.6s-.1-3.1 3.1-3.1h5.3s3 0 3-3V34s.4-3-5-3zm-1.5 1.6c.5 0 .9.4.9.9s-.4.9-.9.9-.9-.4-.9-.9.4-.9.9-.9z" fill="#38bdf8"/>
    <path d="M59 58c5.5 0 5.2-2.4 5.2-2.4l-.01-2.5h-5.3v-.7h7.4s3.5.4 3.5-5.2-3.1-5.1-3.1-5.1h-1.8v2.6s.1 3.1-3.1 3.1h-5.3s-3 0-3 3V55s-.4 3 5 3zm1.5-1.6c-.5 0-.9-.4-.9-.9s.4-.9.9-.9.9.4.9.9-.4.9-.9.9z" fill="#facc15"/>
  </g>

  <!-- AI / Neural Brain Sticker -->
  <g class="sticker" filter="url(#sticker-glow)">
    <animateTransform attributeName="transform" type="translate" values="0,0; 0,5; 0,0" dur="5s" repeatCount="indefinite"/>
    <rect x="94" y="80" width="44" height="44" rx="12" fill="#1e1b4b" fill-opacity="0.75" stroke="#c084fc" stroke-width="1.2" stroke-opacity="0.6"/>
    <circle cx="116" cy="98" r="5" fill="#c084fc"/>
    <circle cx="106" cy="110" r="4" fill="#818cf8"/>
    <circle cx="126" cy="110" r="4" fill="#38bdf8"/>
    <line x1="116" y1="98" x2="106" y2="110" stroke="#c084fc" stroke-width="1.5"/>
    <line x1="116" y1="98" x2="126" y2="110" stroke="#c084fc" stroke-width="1.5"/>
    <line x1="106" y1="110" x2="126" y2="110" stroke="#818cf8" stroke-width="1.5"/>
  </g>

  <!-- C++ Sticker -->
  <g class="sticker" filter="url(#sticker-glow)">
    <animateTransform attributeName="transform" type="translate" values="0,0; 0,-4; 0,0" dur="4.6s" repeatCount="indefinite"/>
    <rect x="22" y="88" width="48" height="38" rx="10" fill="#0f172a" fill-opacity="0.75" stroke="#0284c7" stroke-width="1.2" stroke-opacity="0.6"/>
    <text x="46" y="113" text-anchor="middle" font-family="{MONO}" font-size="14" font-weight="800" fill="#38bdf8">C++</text>
  </g>

  <!-- Right Floating Stickers (PNG-style transparent icons) -->
  <!-- Rocket / FastAPI Sticker -->
  <g class="sticker" filter="url(#sticker-glow)">
    <animateTransform attributeName="transform" type="translate" values="0,0; 0,-5; 0,0" dur="4.8s" repeatCount="indefinite"/>
    <rect x="818" y="24" width="46" height="46" rx="12" fill="#064e3b" fill-opacity="0.7" stroke="#34d399" stroke-width="1.2" stroke-opacity="0.6"/>
    <!-- Rocket vector -->
    <path d="M848 37c-3-3-8-4-13-2l-3 3 7 7 3-3c2-5 1-10-2-13l8-8c1-1 3-1 4 0s1 3 0 4l-4 4z" fill="#34d399"/>
    <path d="M832 45l-3 7 4 4 7-3-8-8z" fill="#6ee7b7"/>
    <circle cx="839" cy="43" r="1.5" fill="#064e3b"/>
  </g>

  <!-- PostgreSQL / Database Cylinder Sticker -->
  <g class="sticker" filter="url(#sticker-glow)">
    <animateTransform attributeName="transform" type="translate" values="0,0; 0,6; 0,0" dur="4.4s" repeatCount="indefinite"/>
    <rect x="762" y="80" width="44" height="44" rx="12" fill="#0c4a6e" fill-opacity="0.75" stroke="#38bdf8" stroke-width="1.2" stroke-opacity="0.6"/>
    <ellipse cx="784" cy="95" rx="11" ry="3.5" fill="#38bdf8"/>
    <path d="M773 95v7c0 2 5 3.5 11 3.5s11-1.5 11-3.5v-7" fill="none" stroke="#38bdf8" stroke-width="1.5"/>
    <path d="M773 103v7c0 2 5 3.5 11 3.5s11-1.5 11-3.5v-7" fill="none" stroke="#38bdf8" stroke-width="1.5"/>
  </g>

  <!-- IIIT Pune Emblem Sticker -->
  <g class="sticker" filter="url(#sticker-glow)">
    <animateTransform attributeName="transform" type="translate" values="0,0; 0,-4; 0,0" dur="5.2s" repeatCount="indefinite"/>
    <rect x="828" y="88" width="50" height="38" rx="10" fill="#451a03" fill-opacity="0.75" stroke="#f59e0b" stroke-width="1.2" stroke-opacity="0.6"/>
    <text x="853" y="112" text-anchor="middle" font-family="{MONO}" font-size="12" font-weight="800" fill="#fbbf24">IIITP</text>
  </g>

  <!-- Center Hero Typography (Transparent, no card) -->
  <text x="{W / 2}" y="32" text-anchor="middle" font-family="{MONO}" font-size="13" font-weight="600" class="f-blue" letter-spacing="2">&lt;DEVELOPER / PORTFOLIO&gt;</text>
  <text x="{W / 2}" y="76" text-anchor="middle" font-family="{SANS}" font-size="{fs_name}" font-weight="900" fill="url(#name-grad)">{name}</text>
  <text x="{W / 2}" y="98" text-anchor="middle" font-family="{SANS}" font-size="13" font-weight="600" class="mu" letter-spacing="1.2">IIIT PUNE '27 &nbsp;•&nbsp; AI &amp; ML &nbsp;•&nbsp; BACKEND &nbsp;•&nbsp; COMPETITIVE PROGRAMMING</text>

  <!-- Animated Typewriter Role -->
  {''.join(parts)}
</svg>"""
    write(ASSETS / "banners" / "hero.svg", svg)


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
# CodeChef: NATIVE PLATFORM UI (transparent background, minimal border)
# ----------------------------------------------------------------------------
def codechef() -> None:
    c = CODECHEF
    W, H = 440, 155
    stars = f"{c['stars']}★"
    nxt = f"{c['next_stars']}★"
    lo = 1400
    hi = c["next_rating"]
    frac = max(0.0, min(1.0, (c["rating"] - lo) / (hi - lo)))
    gap = hi - c["rating"]
    bw = 396

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="CodeChef {c['user']}: rating {c['rating']}, {stars}">
  <style>
    {THEME_CSS}
    .cc-badge {{ fill: #1E7D22; }}
    .cc-green {{ fill: #1E7D22; }}
    @media (prefers-color-scheme: dark) {{
      .cc-green {{ fill: #3fb950; }}
      .cc-badge {{ fill: #238636; }}
    }}
  </style>
  <!-- Minimal clean frame, transparent background -->
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="8" fill="none" class="ln"/>

  <!-- Native CodeChef Profile Header -->
  <rect x="20" y="16" width="34" height="20" rx="4" class="cc-badge"/>
  <text x="37" y="30.5" text-anchor="middle" font-family="{SANS}" font-size="12" font-weight="700" fill="#ffffff">{stars}</text>
  <text x="62" y="31" font-family="{SANS}" font-size="16" font-weight="700" class="tx">{escape(c['user'])}</text>
  <text x="180" y="30.5" font-family="{SANS}" font-size="12" class="mu">(Div 3)</text>
  <text x="{W - 20}" y="30" text-anchor="end" font-family="{MONO}" font-size="11" letter-spacing="1.5" class="mu">CODECHEF</text>

  <line x1="20" y1="44" x2="{W - 20}" y2="44" class="ln"/>

  <!-- Native Stats Layout -->
  <text x="20" y="64" font-family="{SANS}" font-size="11.5" class="mu">Contest Rating</text>
  <text x="20" y="94" font-family="{SANS}" font-size="32" font-weight="800" class="cc-green">{c['rating']}</text>
  <text x="20" y="108" font-family="{SANS}" font-size="11" class="mu">(Highest Rating {c['rating']})</text>

  <text x="235" y="64" font-family="{SANS}" font-size="11.5" class="mu">Contests Participated</text>
  <text x="235" y="94" font-family="{SANS}" font-size="32" font-weight="800" class="tx">{c['contests']}</text>
  <text x="235" y="108" font-family="{SANS}" font-size="11" class="mu">Starters 260 &nbsp;•&nbsp; Rank 637</text>

  <!-- Progress to next star -->
  <text x="20" y="127" font-family="{SANS}" font-size="11.5" class="tx"><tspan font-weight="700" class="cc-green">{gap} pts</tspan> to {nxt} ({hi})<tspan class="mu">  /  {c['contests_needed']} contests (est.)</tspan></text>
  <rect x="20" y="134" width="{bw}" height="6" rx="3" fill="#8b949e" fill-opacity="0.2"/>
  <rect x="20" y="134" width="{bw * frac:.1f}" height="6" rx="3" class="cc-badge"/>
  <text x="20" y="149" font-family="{SANS}" font-size="9.5" class="mu">{stars} 1400</text>
  <text x="{W - 20}" y="149" text-anchor="end" font-family="{SANS}" font-size="9.5" class="mu">{nxt} {hi}</text>
</svg>"""
    write(ASSETS / "profiles" / "codechef.svg", svg)


# ----------------------------------------------------------------------------
# Codeforces: NATIVE PLATFORM UI (transparent background, minimal border)
# ----------------------------------------------------------------------------
def codeforces() -> None:
    c = CODEFORCES
    W, H = 440, 155
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Codeforces {c['user']}: {c['rank']}, rating {c['rating']}">
  <style>
    {THEME_CSS}
    .cf-pupil {{ fill: #008000; }}
    @media (prefers-color-scheme: dark) {{
      .cf-pupil {{ fill: #3fb950; }}
    }}
  </style>
  <!-- Minimal clean frame, transparent background -->
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="8" fill="none" class="ln"/>

  <!-- Native Codeforces 3-bar logo -->
  <rect x="20" y="20" width="4" height="12" rx="1" fill="#F3B431"/>
  <rect x="26" y="16" width="4" height="16" rx="1" fill="#2C65A4"/>
  <rect x="32" y="18" width="4" height="14" rx="1" fill="#C4362E"/>
  <text x="44" y="29.5" font-family="{MONO}" font-size="11" font-weight="700" letter-spacing="1.2" class="mu">CODEFORCES</text>

  <!-- Rank in native Codeforces font -->
  <text x="{W - 20}" y="29" text-anchor="end" font-family="{SANS}" font-size="13" font-weight="700" class="cf-pupil">{escape(c['rank'])}</text>

  <line x1="20" y1="42" x2="{W - 20}" y2="42" class="ln"/>

  <!-- Native user handle in bold green Pupil color -->
  <text x="20" y="66" font-family="{SANS}" font-size="20" font-weight="700" class="cf-pupil">{escape(c['user'])}</text>
  <text x="20" y="82" font-family="{SANS}" font-size="11.5" class="mu">Indian Institute of Information Technology, Pune</text>

  <!-- Native Details List -->
  <text x="20" y="104" font-family="{SANS}" font-size="12" class="mu">Contest rating:</text>
  <text x="140" y="104" font-family="{SANS}" font-size="12" font-weight="700" class="cf-pupil">{c['rating']}</text>
  <text x="175" y="104" font-family="{SANS}" font-size="11" class="mu">(max. {c['rank'].lower()}, {c['max_rating']})</text>

  <text x="20" y="124" font-family="{SANS}" font-size="12" class="mu">Contests participated:</text>
  <text x="165" y="124" font-family="{SANS}" font-size="12" font-weight="700" class="tx">{c['contests']}</text>
  <text x="195" y="124" font-family="{SANS}" font-size="11" class="mu">(latest: Educational Round 195)</text>

  <text x="20" y="143" font-family="{SANS}" font-size="11.5" class="mu">Contribution: <tspan class="tx" font-weight="700">0</tspan> &nbsp;•&nbsp; Location: <tspan class="tx" font-weight="600">Pune, India</tspan></text>
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
    ending()
    for f, t, a in HEADINGS:
        heading(f, t, a)
    availability()
    achievements()
    codechef()
    codeforces()


if __name__ == "__main__":
    main()

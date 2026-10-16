#!/usr/bin/env python3
"""
Generates the SVG assets used by the profile README.

    python tools/generate_assets.py        # everything except the snake
    python tools/generate_snake.py         # contribution snake (needs network)

Output layout
  assets/banners/        hero.svg (typewriter intro), ending.svg (typewriter quotes)
  assets/headings/       one bold, coloured typewriter heading per section
  assets/about/          terminal.svg (animated terminal card)
  assets/status/         availability.svg
  assets/achievements/   achievements.svg
  assets/profiles/       codechef.svg, codeforces.svg  (edit the CONFIG block, re-run)
  assets/snake/          snake.svg (from generate_snake.py)

Every file is self-contained SVG with transparent backgrounds. Colours adapt to
GitHub light / dark mode through `prefers-color-scheme`. Animation is SMIL, so
GitHub renders it through a plain <img> tag.
"""
import shutil
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# ----------------------------------------------------------------------------
# CONFIG: edit and re-run
# ----------------------------------------------------------------------------
CODECHEF = dict(
    user="divyanshindian", rating=1570, stars=2,
    contests=None,                      # <- fill in: contests participated (None shows an em dash)
    next_stars=3, next_rating=1600,
    contests_needed="~1-2",             # rough estimate of contests to reach the next star
)
CODEFORCES = dict(
    user="divyansh.indian1", rating=1240, rank="Pupil",
    contests=None,                      # <- fill in: contests participated (None shows an em dash)
)

HEADINGS = [  # file, text, accent
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
    "B.Tech CSE @ IIIT Pune",
    "AI / ML engineer: RAG, LLM apps",
    "Backend developer: FastAPI, PostgreSQL",
    "Competitive programmer in C++",
    "Open to internships and full-time roles",
]

QUOTES = [  # text, author, accent
    ("Talk is cheap. Show me the code.", "Linus Torvalds", "blue"),
    ("First, solve the problem. Then, write the code.", "John Johnson", "green"),
    ("Make it work, make it right, make it fast.", "Kent Beck", "orange"),
    ("Premature optimization is the root of all evil.", "Donald Knuth", "purple"),
    ("Code. Fail. Learn. Repeat.", "my motto", "pink"),
]
CLOSING = "Thanks for stopping by. Happy coding!"

# ----------------------------------------------------------------------------
# theme helpers (light / dark aware, transparent backgrounds)
# ----------------------------------------------------------------------------
MONO = "'Fira Code','JetBrains Mono','SFMono-Regular',Consolas,'Courier New',monospace"
SANS = "'Segoe UI',Inter,'Helvetica Neue',Arial,sans-serif"

ACCENTS = {  # name: (light, dark)
    "blue": ("#0969da", "#58a6ff"),
    "green": ("#1a7f37", "#3fb950"),
    "purple": ("#8250df", "#bc8cff"),
    "orange": ("#bc4c00", "#f0883e"),
    "pink": ("#bf3989", "#f778ba"),
}

THEME_CSS = (
    "".join(f".f-{k}{{fill:{v[0]}}}.s-{k}{{stroke:{v[0]}}}" for k, v in ACCENTS.items())
    + ".tx{fill:#1f2328}.mu{fill:#656d76}.ln{stroke:#8b949e;stroke-opacity:.35}"
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


# ----------------------------------------------------------------------------
# typewriter primitive: stepped clip reveal + moving block cursor
#   events: [(time_seconds, chars_visible), ...] ascending, first time > 0
#   The text is forced to n * 0.6 * font-size wide (textLength) so the reveal and
#   the cursor line up in any monospace fallback font.
# ----------------------------------------------------------------------------
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


def type_events(t0, n, dt):
    return [(t0 + i * dt, i + 1) for i in range(n)]


# ----------------------------------------------------------------------------
# section headings: bold, coloured, typed once per loop, then a thin rule
# ----------------------------------------------------------------------------
def heading(fname: str, title: str, accent: str) -> None:
    W, H, fs, T = 900, 54, 28, 16
    n = len(title)
    xs = (W - n * fs * 0.6) / 2
    ev = type_events(0.4, n, 0.07) + [(T - 0.5, 0)]
    body = typed(f"h-{fname}", title, xs, 36, fs, f"f-{accent}", T, ev)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(title)}">
  <style>{THEME_CSS}</style>
  {body}
  <line x1="40" y1="{H - 4}" x2="{W - 40}" y2="{H - 4}" class="ln" stroke-width="1"/>
</svg>"""
    write(ASSETS / "headings" / f"{fname}.svg", svg)


# ----------------------------------------------------------------------------
# hero: bold coloured name + cycling typewriter roles (type, hold, erase)
# ----------------------------------------------------------------------------
def hero() -> None:
    W, H = 900, 150
    slot = 5.2
    T = slot * len(HERO_ROLES)
    name = "Divyansh Nagar"
    fs_name = 46
    parts = []
    for i, role in enumerate(HERO_ROLES):
        n, fs = len(role), 22
        xs = (W - n * fs * 0.6) / 2
        t0 = i * slot + 0.3
        ev = type_events(t0, n, 0.045)
        hold_end = ev[-1][0] + 1.9
        ev += [(hold_end + j * 0.02, n - 1 - j) for j in range(n)]
        parts.append(typed(f"r{i}", role, xs, 112, fs, "f-green", T, ev, weight=500))
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Divyansh Nagar: AI, backend and competitive programming">
  <style>{THEME_CSS}</style>
  <text x="{W / 2}" y="62" text-anchor="middle" font-family="{SANS}" font-size="{fs_name}" font-weight="800" class="f-blue">{name}</text>
  {''.join(parts)}
</svg>"""
    write(ASSETS / "banners" / "hero.svg", svg)


# ----------------------------------------------------------------------------
# ending: quotes typed one after another, author fades in
# ----------------------------------------------------------------------------
def ending() -> None:
    W, H = 900, 110
    slot = 7.0
    items = [(q, a, c) for q, a, c in QUOTES] + [(CLOSING, None, "blue")]
    T = slot * len(items)
    parts = []
    for i, (text, author, accent) in enumerate(items):
        shown = f"\u201c{text}\u201d" if author else text
        n, fs = len(shown), 20
        xs = (W - n * fs * 0.6) / 2
        t0 = i * slot + 0.3
        ev = type_events(t0, n, 0.04)
        hold_end = ev[-1][0] + 3.2
        ev += [(hold_end + j * 0.012, n - 1 - j) for j in range(n)]
        parts.append(typed(f"q{i}", shown, xs, 50, fs, f"f-{accent}", T, ev))
        if author:
            a0 = ev[n - 1][0] + 0.2
            a1 = hold_end
            parts.append(
                f'<text x="{W / 2}" y="82" text-anchor="middle" font-family="{MONO}" font-size="14" class="mu" opacity="0">'
                f'\u2014 {escape(author)}'
                f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{a0 / T:.4f};{(a0 + 0.4) / T:.4f};{a1 / T:.4f};{(a1 + 0.3) / T:.4f};1" dur="{T}s" repeatCount="indefinite"/></text>'
            )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Closing quotes about programming">
  <style>{THEME_CSS}</style>
  <line x1="40" y1="4" x2="{W - 40}" y2="4" class="ln" stroke-width="1"/>
  {''.join(parts)}
</svg>"""
    write(ASSETS / "banners" / "ending.svg", svg)


# ----------------------------------------------------------------------------
# About Me: animated terminal (always dark, like a real terminal)
# ----------------------------------------------------------------------------
def terminal() -> None:
    W = 860
    LH, y0 = 23, 76
    G, FG, MU, BL = "#3fb950", "#e6edf3", "#8b949e", "#58a6ff"
    # ("cmd", text) | ("out", [(text, colour), ...]) | ("idle",)
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
            px = 28 + 2 * cw  # after "$ "
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
        else:  # idle prompt with a blinking cursor until the loop restarts
            rows.append(
                f'<g opacity="0"><animate attributeName="opacity" calcMode="discrete" values="0;1" keyTimes="0;{t / T:.4f}" dur="{T}s" repeatCount="indefinite"/>'
                f'<text x="28" y="{y}" font-family="{MONO}" font-size="{fs}" fill="{G}" font-weight="700">$</text>'
                f'<rect x="{28 + 2 * cw:.1f}" y="{y - 12}" width="8" height="16" fill="{FG}" opacity="0.85"><animate attributeName="opacity" values="0.85;0;0.85" dur="1s" repeatCount="indefinite"/></rect></g>'
            )
            t += 3
    assert t < T - 2, f"timeline {t:.1f}s overruns the {T}s loop"
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
# availability (single line, pulsing dot)
# ----------------------------------------------------------------------------
def availability() -> None:
    W, H = 900, 40
    msg = "Open to internships and full-time opportunities"
    fs = 16
    tw = len(msg) * fs * 0.6
    x = (W - tw - 26) / 2
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{msg}">
  <style>{THEME_CSS}</style>
  <circle cx="{x + 6:.1f}" cy="21" r="5" class="f-green"/>
  <circle cx="{x + 6:.1f}" cy="21" r="5" class="s-green" fill="none" stroke-width="2">
    <animate attributeName="r" values="5;13" dur="1.8s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.8;0" dur="1.8s" repeatCount="indefinite"/>
  </circle>
  <text x="{x + 26:.1f}" y="27" font-family="{MONO}" font-size="{fs}" font-weight="700" class="f-green" textLength="{tw:.1f}" lengthAdjust="spacing">{msg}</text>
</svg>"""
    write(ASSETS / "status" / "availability.svg", svg)


# ----------------------------------------------------------------------------
# achievements: plain typographic grid, no cards
# ----------------------------------------------------------------------------
def achievements() -> None:
    items = [  # metric, accent, title, line1, line2
        ("AIR 43", "green", "Naukri EROH 2025", "Round 2, 6,000+ participants", "AI in Renewable Energy"),
        ("Top 10%", "blue", "ISRO BAH 2025", "500+ teams", "Aditya-L1 Halo CME detection"),
        ("CS50x", "purple", "Harvard University", "Introduction to Computer Science", "C, Python, SQL, algorithms, memory"),
        ("Rank 1621", "orange", "CodeChef Starters 225", "Global rank", "Rated 2 star on CodeChef"),
        ("97.81 %ile", "pink", "JEE Main 2023", "About 1 million candidates", "National engineering entrance"),
        ("300+", "blue", "DSA problems solved", "Practised mainly in C++", "Rated on 3 platforms"),
    ]
    W, colw, rowh = 900, 300, 112
    H = rowh * 2 + 6
    out = []
    for i, (m, acc, title, l1, l2) in enumerate(items):
        x = (i % 3) * colw + 28
        y = (i // 3) * rowh
        out.append(
            f'<text x="{x}" y="{y + 38}" font-family="{SANS}" font-size="30" font-weight="800" class="f-{acc}">{escape(m)}</text>'
            f'<text x="{x}" y="{y + 62}" font-family="{SANS}" font-size="15" font-weight="700" class="tx">{escape(title)}</text>'
            f'<text x="{x}" y="{y + 82}" font-family="{SANS}" font-size="12.5" class="mu">{escape(l1)}</text>'
            f'<text x="{x}" y="{y + 99}" font-family="{SANS}" font-size="12.5" class="mu">{escape(l2)}</text>'
        )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Achievements: AIR 43 Naukri EROH, ISRO BAH top 10 percent, Harvard CS50x, CodeChef rank 1621, JEE Main 97.81 percentile, 300+ DSA problems">
  <style>{THEME_CSS}</style>
  {''.join(out)}
</svg>"""
    write(ASSETS / "achievements" / "achievements.svg", svg)


# ----------------------------------------------------------------------------
# platform cards, modelled on each site's own profile page
# ----------------------------------------------------------------------------
CARD_CSS = (
    THEME_CSS
    + ".bd{stroke:#8b949e;stroke-opacity:.4}.track{fill:#8b949e;fill-opacity:.25}"
    + ".cc2{fill:#1e7d22}.cf-pupil{fill:#008000}"
    + "@media (prefers-color-scheme: dark){.cc2{fill:#3fb950}.cf-pupil{fill:#3fb950}}"
)


def codechef() -> None:
    c = CODECHEF
    W, H = 440, 170
    stars = f"{c['stars']}\u2605"
    nxt = f"{c['next_stars']}\u2605"
    lo = {1: 0, 2: 1400, 3: 1600}[c["stars"]]
    frac = (c["rating"] - lo) / (c["next_rating"] - lo)
    gap = c["next_rating"] - c["rating"]
    bw = 400
    contests = "\u2014" if c["contests"] is None else str(c["contests"])
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="CodeChef {c['user']}: rating {c['rating']}, {c['stars']} star">
  <style>{CARD_CSS}</style>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="6" fill="none" class="bd"/>
  <rect x="20" y="16" width="38" height="22" rx="4" class="cc2"/>
  <text x="39" y="32" text-anchor="middle" font-family="{SANS}" font-size="13" font-weight="700" fill="#fff">{stars}</text>
  <text x="68" y="33" font-family="{SANS}" font-size="18" font-weight="700" class="tx">{escape(c['user'])}</text>
  <text x="{W - 20}" y="32" text-anchor="end" font-family="{MONO}" font-size="11" letter-spacing="1.5" class="mu">CODECHEF</text>
  <line x1="20" y1="48" x2="{W - 20}" y2="48" class="ln"/>
  <text x="20" y="72" font-family="{SANS}" font-size="11.5" class="mu">Rating</text>
  <text x="20" y="104" font-family="{SANS}" font-size="34" font-weight="800" class="cc2">{c['rating']}</text>
  <text x="240" y="72" font-family="{SANS}" font-size="11.5" class="mu">No. of contests participated</text>
  <text x="240" y="104" font-family="{SANS}" font-size="34" font-weight="800" class="tx">{contests}</text>
  <text x="20" y="130" font-family="{SANS}" font-size="12" class="tx"><tspan font-weight="700">{gap} points</tspan> to {nxt} ({c['next_rating']})<tspan class="mu">  /  {c['contests_needed']} contests (est.)</tspan></text>
  <rect x="20" y="138" width="{bw}" height="7" rx="3.5" class="track"/>
  <rect x="20" y="138" width="{bw * frac:.1f}" height="7" rx="3.5" class="cc2"/>
  <text x="20" y="160" font-family="{SANS}" font-size="10.5" class="mu">{stars} 1400</text>
  <text x="{W - 20}" y="160" text-anchor="end" font-family="{SANS}" font-size="10.5" class="mu">{nxt} {c['next_rating']}</text>
</svg>"""
    write(ASSETS / "profiles" / "codechef.svg", svg)


def codeforces() -> None:
    c = CODEFORCES
    W, H = 440, 170
    contests = "\u2014" if c["contests"] is None else str(c["contests"])
    rows = [("Contest rating:", str(c["rating"]), True), ("Rank:", c["rank"], True), ("Contests participated:", contests, False)]
    body = []
    for i, (k, v, colored) in enumerate(rows):
        y = 108 + i * 24
        body.append(
            f'<text x="20" y="{y}" font-family="{SANS}" font-size="14" class="mu">{k}</text>'
            f'<text x="190" y="{y}" font-family="{SANS}" font-size="14" font-weight="700" class="{"cf-pupil" if colored else "tx"}">{escape(v)}</text>'
        )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Codeforces {c['user']}: {c['rank']}, rating {c['rating']}">
  <style>{CARD_CSS}</style>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="6" fill="none" class="bd"/>
  <text x="20" y="32" font-family="{SANS}" font-size="14" font-weight="700" class="cf-pupil">{escape(c['rank'])}</text>
  <text x="{W - 20}" y="30" text-anchor="end" font-family="{MONO}" font-size="11" letter-spacing="1.5" class="mu">CODEFORCES</text>
  <text x="20" y="64" font-family="{SANS}" font-size="26" font-weight="700" class="cf-pupil">{escape(c['user'])}</text>
  <line x1="20" y1="80" x2="{W - 20}" y2="80" class="ln"/>
  {''.join(body)}
</svg>"""
    write(ASSETS / "profiles" / "codeforces.svg", svg)


def main() -> None:
    # remove assets from the previous design (the snake folder is kept)
    for sub in ("banners", "headings", "profiles", "highlights", "about", "status", "achievements"):
        shutil.rmtree(ASSETS / sub, ignore_errors=True)
    hero()
    ending()
    for f, t, a in HEADINGS:
        heading(f, t, a)
    terminal()
    availability()
    achievements()
    codechef()
    codeforces()


if __name__ == "__main__":
    main()

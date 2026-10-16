#!/usr/bin/env python3
"""
Contribution snake for the LAST ~4 MONTHS of GitHub activity.

    python tools/generate_snake.py [github_username]

Reads the public contribution calendar (no token needed), keeps the most recent
18 week-columns (about 4 months) and writes one self-contained, theme-aware SVG:

    assets/snake/snake.svg

The snake walks the grid column by column and "eats" every contribution square.
Re-run it (or let .github/workflows/snake.yml do it daily) to refresh.
"""
import re
import sys
import urllib.request
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "snake" / "snake.svg"

WEEKS = 28            # ~ 6.5 months
PITCH, SIZE = 30, 26  # cell pitch / cell size (px)
MOVE_SECONDS = 28     # snake travel time
PAUSE_SECONDS = 3     # rest before the loop restarts
SNAKE_CELLS = 6       # snake length in cells


def fetch(user: str) -> dict:
    url = f"https://github.com/users/{user}/contributions"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
    days = {}
    for tag in re.findall(r"<td[^>]*ContributionCalendar-day[^>]*>", html):
        d = re.search(r'data-date="(\d{4}-\d{2}-\d{2})"', tag)
        l = re.search(r'data-level="(\d)"', tag)
        if d and l:
            days[date.fromisoformat(d.group(1))] = int(l.group(1))
    if not days:
        raise SystemExit("Could not read the contribution calendar.")
    return days


def build(days: dict) -> str:
    last = max(days)
    sunday = lambda d: d - timedelta(days=(d.weekday() + 1) % 7)
    first_col = sunday(last) - timedelta(weeks=WEEKS - 1)

    cells = {}  # (col, row) -> (date, level)
    for d, lvl in days.items():
        if d < first_col:
            continue
        col = (sunday(d) - first_col).days // 7
        row = (d.weekday() + 1) % 7
        cells[(col, row)] = (d, lvl)

    x0, y0 = 30, 38
    W = x0 * 2 + WEEKS * PITCH
    H = y0 + 7 * PITCH + 22
    cx = lambda c: x0 + c * PITCH + PITCH / 2
    cy = lambda r: y0 + r * PITCH + PITCH / 2

    # ---- snake route: down column 0, up column 1, ... (plus lead-in / lead-out)
    route = []
    for c in range(WEEKS):
        rows = range(7) if c % 2 == 0 else range(6, -1, -1)
        route += [(cx(c), cy(r), (c, r)) for r in rows]
    pts = [(-12, cy(0))] + [(x, y) for x, y, _ in route] + [(W + 12, route[-1][1])]
    dist, total = [0.0], 0.0
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        total += abs(bx - ax) + abs(by - ay)
        dist.append(total)
    d_of = {key: dist[i + 1] for i, (_, _, key) in enumerate(route)}
    path_d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)

    S = SNAKE_CELLS * PITCH
    T = MOVE_SECONDS + PAUSE_SECONDS
    move_frac = MOVE_SECONDS / T
    reach = total / (total + S)  # fraction of the move at which the head ends the path

    # ---- grid
    base, eat = [], []
    for (c, r), (d, lvl) in sorted(cells.items()):
        x, y = x0 + c * PITCH + (PITCH - SIZE) / 2, y0 + r * PITCH + (PITCH - SIZE) / 2
        base.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{SIZE}" height="{SIZE}" rx="4" class="l0"/>')
        if lvl > 0:
            tk = d_of[(c, r)] / (total + S) * move_frac
            a, b = min(tk, 0.995), min(tk + 0.004, 0.999)
            eat.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{SIZE}" height="{SIZE}" rx="4" class="l{lvl}">'
                f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;{a:.4f};{b:.4f};1" '
                f'dur="{T}s" repeatCount="indefinite"/></rect>'
            )

    # ---- month labels
    labels, seen = [], None
    for c in range(WEEKS):
        d = first_col + timedelta(weeks=c)
        if d.month != seen and (d + timedelta(days=6)).month == d.month or c == 0:
            if d.month != seen:
                labels.append(f'<text x="{x0 + c * PITCH}" y="{y0 - 12}" class="mut">{d.strftime("%b")}</text>')
                seen = d.month

    head_dur = f"{T * move_frac * 1:.2f}"
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Snake eating my GitHub contributions from the last four months">
  <style>
    .l0{{fill:#ebedf0}} .l1{{fill:#9be9a8}} .l2{{fill:#40c463}} .l3{{fill:#30a14e}} .l4{{fill:#216e39}}
    .snake{{stroke:#0ea5e9}} .head{{fill:#0284c7}} .eye{{fill:#fff}}
    .mut{{fill:#656d76;font:12px 'Segoe UI',Arial,sans-serif}}
    @media (prefers-color-scheme: dark) {{
      .l0{{fill:#161b22}} .l1{{fill:#0e4429}} .l2{{fill:#006d32}} .l3{{fill:#26a641}} .l4{{fill:#39d353}}
      .snake{{stroke:#38bdf8}} .head{{fill:#7dd3fc}} .eye{{fill:#0d1117}}
      .mut{{fill:#8b949e}}
    }}
  </style>
  <clipPath id="view"><rect width="{W}" height="{H}"/></clipPath>
  <g clip-path="url(#view)">
    {''.join(labels)}
    {''.join(base)}
    {''.join(eat)}
    <path d="{path_d}" class="snake" fill="none" stroke-width="{SIZE - 8}" stroke-linecap="round" stroke-linejoin="round"
          stroke-dasharray="{S} {total + S:.1f}" stroke-dashoffset="{S}">
      <animate attributeName="stroke-dashoffset" values="{S};{-total:.1f};{-total:.1f}" keyTimes="0;{move_frac:.4f};1" dur="{T}s" repeatCount="indefinite"/>
    </path>
    <g>
      <circle r="{(SIZE - 4) / 2}" class="head"/>
      <circle cx="3" cy="-4" r="2.2" class="eye"/><circle cx="3" cy="4" r="2.2" class="eye"/>
      <animateMotion dur="{T}s" repeatCount="indefinite" rotate="auto" calcMode="linear"
                     keyPoints="0;1;1" keyTimes="0;{reach * move_frac:.4f};1" path="{path_d}"/>
    </g>
  </g>
</svg>"""
    return svg


def main() -> None:
    user = sys.argv[1] if len(sys.argv) > 1 else "inddivyansh"
    svg = build(fetch(user))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg + "\n", encoding="utf-8")
    print("wrote", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()

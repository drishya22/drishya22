"""
Hand-authored neofetch-style info card SVG.
This is static content — re-run it only when you want to update the text
(new role, new focus areas, etc). Each row fades/slides in on a stagger.

Writes info-card.svg at the repo root.
"""

from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / "info-card.svg"

USERNAME = "drishya22"

# Edit these freely — this is the only file you need to touch to update
# the "About Me" content.
ROWS = [
    ("Role", "SWE Fellow (AI) @ HeadStarter"),
    ("Mentor", "Course Mentor @ IIT Madras"),
    ("Degrees", "B.Tech CSE (MSIT) + BS Data Science (IIT Madras)"),
    ("Focus", "AI/ML systems, backend APIs, NLP"),
    ("Stack", "Python, PyTorch, FastAPI, Flask, Vue.js"),
    ("Recent", "AI Web App Generator API, Placement Portal"),
    ("Stats", "600+ LeetCode solved (Top 20%)"),
]

TITLE = f"{USERNAME}@github"

WIDTH = 490
LINE_H = 26
TOP_PAD = 46
LEFT_PAD = 22


def build_svg():
    rows_svg = []
    for i, (key, val) in enumerate(ROWS):
        y = TOP_PAD + i * LINE_H
        delay = 0.15 + i * 0.12
        rows_svg.append(
            f'<g class="row" style="animation-delay:{delay:.2f}s">'
            f'<text x="{LEFT_PAD}" y="{y}" class="key">{escape(key)}</text>'
            f'<text x="{LEFT_PAD + 90}" y="{y}" class="val">{escape(val)}</text>'
            f"</g>"
        )

    height = TOP_PAD + len(ROWS) * LINE_H + 20

    svg = f"""<svg viewBox="0 0 {WIDTH} {height}" width="{WIDTH}" height="{height}"
     xmlns="http://www.w3.org/2000/svg" font-family="Consolas, 'Courier New', monospace">
  <style>
    .titlebar {{ fill: #8b949e; font-size: 13px; font-weight: bold; }}
    .rule {{ stroke: #30363d; stroke-width: 1; }}
    .key {{ fill: #39d353; font-size: 13px; font-weight: bold; }}
    .val {{ fill: #c9d1d9; font-size: 13px; }}
    .row {{
      opacity: 0;
      animation: fadein 0.4s ease-out forwards;
    }}
    @keyframes fadein {{
      0%   {{ opacity: 0; transform: translateX(-8px); }}
      100% {{ opacity: 1; transform: translateX(0); }}
    }}
  </style>
  <rect width="100%" height="100%" fill="none" />
  <text x="{LEFT_PAD}" y="24" class="titlebar">{TITLE}</text>
  <line x1="{LEFT_PAD}" y1="34" x2="{WIDTH - LEFT_PAD}" y2="34" class="rule" />
  {''.join(rows_svg)}
</svg>
"""
    return svg


def main():
    OUT_PATH.write_text(build_svg())
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
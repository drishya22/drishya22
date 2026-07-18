"""
Renders data/contributions.json as a 53-week x 7-day heatmap SVG,
styled like GitHub's own contribution graph, with a diagonal
slide-down reveal animation (plays once on load, no looping).

Writes contrib-heatmap.svg at the repo root.
"""

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "contributions.json"
OUT_PATH = ROOT / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

BOX = 11
GAP = 3
LEFT_PAD = 30
TOP_PAD = 20
DAY_LABELS = ["Mon", "", "Wed", "", "Fri", "", ""]


def level_color(level, count):
    if level is not None:
        idx = min(level, len(PALETTE) - 1)
        return PALETTE[idx]
    if count == 0:
        return PALETTE[0]
    if count < 3:
        return PALETTE[1]
    if count < 6:
        return PALETTE[2]
    if count < 10:
        return PALETTE[3]
    return PALETTE[4]


def build_svg(payload):
    days = payload["days"]
    stats = payload["stats"]
    username = payload["username"]

    weeks = []
    week = [None] * 7
    for d in days:
        dt = datetime.strptime(d["date"], "%Y-%m-%d")
        dow = (dt.weekday() + 1) % 7
        if dow == 0 and any(week):
            weeks.append(week)
            week = [None] * 7
        week[dow] = d
    if any(week):
        weeks.append(week)

    n_weeks = len(weeks)
    width = LEFT_PAD + n_weeks * (BOX + GAP) + 20
    height = TOP_PAD + 7 * (BOX + GAP) + 60

    cells_svg = []
    delay_step = 0.004
    i = 0
    for w_idx, week in enumerate(weeks):
        for d_idx, d in enumerate(week):
            if d is None:
                continue
            x = LEFT_PAD + w_idx * (BOX + GAP)
            y = TOP_PAD + d_idx * (BOX + GAP)
            color = level_color(d.get("level"), d.get("count", 0))
            delay = (w_idx + d_idx) * delay_step
            cells_svg.append(
                f'<rect class="cell" x="{x}" y="{y - 8}" width="{BOX}" height="{BOX}" '
                f'rx="2" ry="2" fill="{color}" opacity="0" '
                f'style="animation-delay:{delay:.3f}s">'
                f"<title>{d['date']}: {d.get('count', 0)} contributions</title>"
                f"</rect>"
            )
            i += 1

    day_labels_svg = "".join(
        f'<text x="8" y="{TOP_PAD + idx * (BOX + GAP) + 9}" class="daylabel">{lbl}</text>'
        for idx, lbl in enumerate(DAY_LABELS)
        if lbl
    )

    legend_x = width - 140
    legend_y = height - 20
    legend_boxes = "".join(
        f'<rect x="{legend_x + 32 + idx * (BOX + 3)}" y="{legend_y - 9}" '
        f'width="{BOX}" height="{BOX}" rx="2" fill="{c}" />'
        for idx, c in enumerate(PALETTE[:6])
    )

    footer = (
        f'{stats["total_last_year"]} contributions in the last year &#183; '
        f'current streak {stats["current_streak"]} &#183; '
        f'longest streak {stats["longest_streak"]}'
    )

    svg = f"""<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}"
     xmlns="http://www.w3.org/2000/svg" font-family="Consolas, 'Courier New', monospace">
  <style>
    .cell {{
      animation: reveal 0.5s ease-out forwards;
    }}
    @keyframes reveal {{
      0%   {{ opacity: 0; transform: translate(-6px, -6px); }}
      100% {{ opacity: 1; transform: translate(0, 0); }}
    }}
    .daylabel {{ fill: #8b949e; font-size: 9px; }}
    .footer {{ fill: #8b949e; font-size: 11px; }}
    .legend {{ fill: #8b949e; font-size: 9px; }}
    text {{ dominant-baseline: middle; }}
  </style>
  <rect width="100%" height="100%" fill="none" />
  {day_labels_svg}
  <g>
    {''.join(cells_svg)}
  </g>
  <text x="{LEFT_PAD}" y="{height - 20}" class="footer">{footer}</text>
  <text x="{legend_x}" y="{legend_y}" class="legend">Less</text>
  {legend_boxes}
  <text x="{legend_x + 32 + 6 * (BOX + 3) + 4}" y="{legend_y}" class="legend">More</text>
</svg>
"""
    return svg


def main():
    payload = json.loads(DATA_PATH.read_text())
    svg = build_svg(payload)
    OUT_PATH.write_text(svg)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
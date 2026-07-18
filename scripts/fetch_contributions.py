"""
Fetches the public contribution calendar for a GitHub user with NO token
required, by parsing the same HTML fragment GitHub's own profile page uses.

Writes data/contributions.json with:
  - raw daily counts
  - current streak / longest streak
  - best single day
  - total contributions in the last year
"""

import json
import re
from datetime import datetime, date, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "drishya22"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "contributions.json"


def fetch_days():
    resp = requests.get(URL, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []
    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        cells = soup.select("rect.ContributionCalendar-day")

    for cell in cells:
        d = cell.get("data-date")
        if not d:
            continue
        level = cell.get("data-level")
        tooltip_id = cell.get("id")
        count = 0
        if tooltip_id:
            tooltip = soup.find(attrs={"for": tooltip_id}) or soup.find(
                id=f"{tooltip_id}-tooltip"
            )
            if tooltip:
                m = re.search(r"([\d,]+)\s+contribution", tooltip.get_text())
                if m:
                    count = int(m.group(1).replace(",", ""))
        days.append(
            {
                "date": d,
                "level": int(level) if level is not None else None,
                "count": count,
            }
        )

    days.sort(key=lambda x: x["date"])
    return days


def compute_stats(days):
    total = sum(d["count"] for d in days)

    longest = 0
    running = 0
    for d in days:
        if d["count"] > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0

    running = 0
    for d in reversed(days):
        if d["count"] > 0:
            running += 1
        else:
            break
    current = running

    best_day = max(days, key=lambda x: x["count"], default=None)

    monthly = {}
    for d in days:
        month = d["date"][:7]
        monthly[month] = monthly.get(month, 0) + d["count"]

    return {
        "total_last_year": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best_day,
        "monthly": monthly,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }


def main():
    days = fetch_days()
    if not days:
        raise SystemExit(
            "No contribution cells found — GitHub may have changed its markup. "
            "Check the CSS selectors in fetch_contributions.py."
        )
    stats = compute_stats(days)
    payload = {"username": USERNAME, "days": days, "stats": stats}

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {len(days)} days to {OUT_PATH}")
    print(f"Total: {stats['total_last_year']}  Current streak: {stats['current_streak']}  "
          f"Longest streak: {stats['longest_streak']}")


if __name__ == "__main__":
    main()
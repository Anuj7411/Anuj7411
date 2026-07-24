"""
Step 4a: scrape the PUBLIC contributions calendar (no token/GraphQL needed).
Source: https://github.com/users/<username>/contributions

Usage: python scripts/fetch_contributions.py [github_username]
Output: data/contributions.json
"""
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

DEFAULT_USERNAME = "Anuj7411"
URL_TMPL = "https://github.com/users/{username}/contributions"
HEADERS = {"User-Agent": "Mozilla/5.0 (profile-readme-bot)"}


def fetch_html(username: str) -> str:
    resp = requests.get(URL_TMPL.format(username=username), headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.text


def parse_days(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    days = []

    # GitHub renders each day as a <td> (older) or <rect>/<td> with data-date + either
    # data-level (0-4) or a tooltip/aria-label containing the contribution count.
    cells = soup.select("[data-date]")
    for cell in cells:
        d = cell.get("data-date")
        if not d:
            continue

        level = cell.get("data-level")
        count = None

        # Try aria-label / tooltip text first: "3 contributions on January 5th."
        label = cell.get("aria-label") or cell.get("title") or cell.text or ""
        m = re.search(r"(\d+)\s+contribution", label)
        if m:
            count = int(m.group(1))
        elif re.search(r"no contribution", label, re.IGNORECASE):
            count = 0

        if count is None and level is not None:
            # Fall back to level-based estimate if no count text is present
            level_i = int(level)
            count = [0, 1, 3, 6, 10][min(level_i, 4)]

        if count is None:
            continue

        days.append({"date": d, "count": count, "level": int(level) if level is not None else None})

    days.sort(key=lambda x: x["date"])
    return days


def compute_stats(days: list[dict]) -> dict:
    if not days:
        return {
            "days": [],
            "current_streak": 0,
            "longest_streak": 0,
            "best_day": None,
            "monthly_totals": {},
            "year_total": 0,
        }

    # Streaks
    longest = current = 0
    running = 0
    for d in days:
        if d["count"] > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0
    # current streak = trailing run ending today/most-recent day
    for d in reversed(days):
        if d["count"] > 0:
            current += 1
        else:
            break

    best_day = max(days, key=lambda x: x["count"])

    monthly_totals: dict[str, int] = {}
    for d in days:
        month_key = d["date"][:7]  # YYYY-MM
        monthly_totals[month_key] = monthly_totals.get(month_key, 0) + d["count"]

    year_total = sum(d["count"] for d in days)

    return {
        "days": days,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best_day,
        "monthly_totals": monthly_totals,
        "year_total": year_total,
    }


def main() -> None:
    username = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_USERNAME
    html = fetch_html(username)
    days = parse_days(html)
    stats = compute_stats(days)
    stats["username"] = username
    stats["fetched_at"] = datetime.now(timezone.utc).isoformat()

    Path("data").mkdir(exist_ok=True)
    out_path = Path("data/contributions.json")
    out_path.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}: {len(days)} days, {stats['year_total']} total, "
          f"streak {stats['current_streak']} (longest {stats['longest_streak']})")


if __name__ == "__main__":
    main()

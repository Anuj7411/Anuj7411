"""
Step 4b: draw the 53-week x 7-day contribution grid from data/contributions.json,
with a diagonal reveal animation (SMIL) that plays once then freezes.

Env:   STATIC=1   -> frozen preview (no animation tags)
Output: contrib-heatmap.svg (repo root)
"""
import json
import os
from datetime import date, datetime, timedelta
from pathlib import Path

WEEKS = 53
DAYS = 7
CELL = 12
GAP = 3
MARGIN_LEFT = 30
MARGIN_TOP = 20
MARGIN_BOTTOM = 34

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
BG = "#0d1117"
TEXT_COLOR = "#8b949e"

DIAG_STAGGER_S = 0.012   # delay per (week+day) diagonal step
DIAG_DUR_S = 0.28


def level_for_count(count: int) -> int:
    if count <= 0:
        return 0
    if count <= 2:
        return 1
    if count <= 5:
        return 2
    if count <= 9:
        return 3
    return 4


def build_grid(days: list[dict]) -> dict[str, dict]:
    return {d["date"]: d for d in days}


def main() -> None:
    data_path = Path("data/contributions.json")
    if not data_path.exists():
        raise FileNotFoundError("data/contributions.json not found. Run fetch_contributions.py first.")

    stats = json.loads(data_path.read_text(encoding="utf-8"))
    day_map = build_grid(stats.get("days", []))
    year_total = stats.get("year_total", 0)

    today = date.today()
    # Align the grid so the last column ends on the most recent Saturday-anchored week,
    # matching GitHub's own calendar layout (weeks run Sun -> Sat).
    end = today
    start = end - timedelta(days=WEEKS * 7 - 1)
    start -= timedelta(days=start.weekday() + 1 if start.weekday() != 6 else 0)  # snap to a Sunday

    width = MARGIN_LEFT + WEEKS * (CELL + GAP)
    height = MARGIN_TOP + DAYS * (CELL + GAP) + MARGIN_BOTTOM

    static = os.environ.get("STATIC") == "1"

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}">',
        f'<style>text{{font-family:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace;'
        f'font-size:11px;fill:{TEXT_COLOR};}}</style>',
        f'<rect width="100%" height="100%" fill="{BG}"/>',
    ]

    cursor = start
    for week in range(WEEKS):
        for day in range(DAYS):
            d_str = cursor.strftime("%Y-%m-%d")
            entry = day_map.get(d_str)
            level = entry["level"] if (entry and entry.get("level") is not None) \
                else level_for_count(entry["count"] if entry else 0)
            color = PALETTE[min(level, len(PALETTE) - 1)]

            x = MARGIN_LEFT + week * (CELL + GAP)
            y = MARGIN_TOP + day * (CELL + GAP)

            rect_attrs = f'x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"'

            if static or cursor > today:
                if cursor <= today:
                    parts.append(f'<rect {rect_attrs}/>')
            else:
                begin = (week + day) * DIAG_STAGGER_S
                parts.append(
                    f'<rect {rect_attrs} opacity="0">'
                    f'<animate attributeName="opacity" from="0" to="1" '
                    f'begin="{begin:.3f}s" dur="{DIAG_DUR_S}s" fill="freeze"/>'
                    f'</rect>'
                )

            cursor += timedelta(days=1)

    # Legend: Less [boxes] More
    legend_y = MARGIN_TOP + DAYS * (CELL + GAP) + 18
    legend_x = MARGIN_LEFT
    parts.append(f'<text x="{legend_x}" y="{legend_y + 9}">Less</text>')
    lx = legend_x + 34
    for color in PALETTE:
        parts.append(f'<rect x="{lx}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"/>')
        lx += CELL + GAP
    parts.append(f'<text x="{lx + 4}" y="{legend_y + 9}">More</text>')

    # Footer: yearly total, right-aligned
    footer_txt = f"{year_total} contributions in the last year"
    parts.append(f'<text x="{width - MARGIN_LEFT}" y="{legend_y + 9}" text-anchor="end">{footer_txt}</text>')

    parts.append("</svg>")

    Path("contrib-heatmap.svg").write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote contrib-heatmap.svg ({'static' if static else 'animated'}), total={year_total}")


if __name__ == "__main__":
    main()

"""
Step 3: hand-authored neofetch-style info card SVG.
Content lives in CONTENT below - edit this list whenever your bio changes,
then re-run: python scripts/make_info_card.py

Env:   STATIC=1   -> frozen preview (no animation tags)
Output: info-card.svg (repo root)
"""
import os
from pathlib import Path

WIDTH = 490
BG = "#0d1117"
BORDER = "#30363d"
TITLEBAR = "#161b22"
KEY_COLOR = "#39d353"   # matches the ASCII portrait's green
VAL_COLOR = "#c9d1d9"
DIM_COLOR = "#8b949e"

ROW_H = 26
PAD_X = 20
VALUE_X_OFFSET = 130   # where the value column starts, relative to PAD_X
TITLE_H = 34
FADE_STAGGER_S = 0.12
FADE_DUR_S = 0.4
FONT_SIZE = 13
CHAR_WIDTH_RATIO = 0.62  # approx monospace advance width as a fraction of font-size

# Max characters the value column can hold before it runs off the card edge.
# Auto-computed from WIDTH so widening/narrowing the card keeps this in sync.
MAX_VALUE_CHARS = int((WIDTH - (PAD_X + VALUE_X_OFFSET) - PAD_X) / (FONT_SIZE * CHAR_WIDTH_RATIO))

# EVERGREEN content only - no counts that go stale (those live in the README body).
# key, value  (keep each value short; auto-truncates if it overflows the card).
CONTENT = [
    ("focus", "AI agent tooling . evals . infra"),
    ("based", "Bhopal, India"),
    ("stack", "TypeScript . Python . Rust . Next.js"),
    ("workflow", "ships solo via AI coding-agent pipeline"),
    ("open-to", "founding-track builder / technical PM"),
    ("remote", "yes -- early-stage AI teams"),
]

TITLE = "anuj@github:~$ neofetch"


def escape_xml(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_svg(static: bool) -> str:
    height = TITLE_H + len(CONTENT) * ROW_H + 16

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" '
        f'width="{WIDTH}" height="{height}">',
        f'<style>text{{font-family:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace;'
        f'font-size:{FONT_SIZE}px;}}</style>',
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="8" '
        f'fill="{BG}" stroke="{BORDER}"/>',
        # title bar
        f'<path d="M0.5 8.5 A8 8 0 0 1 8.5 0.5 H{WIDTH - 8.5} A8 8 0 0 1 {WIDTH - 0.5} 8.5 '
        f'V{TITLE_H} H0.5 Z" fill="{TITLEBAR}"/>',
        f'<circle cx="20" cy="{TITLE_H / 2:.0f}" r="5" fill="#ff5f56"/>',
        f'<circle cx="38" cy="{TITLE_H / 2:.0f}" r="5" fill="#ffbd2e"/>',
        f'<circle cx="56" cy="{TITLE_H / 2:.0f}" r="5" fill="#27c93f"/>',
        f'<text x="{PAD_X + 60}" y="{TITLE_H / 2 + 4:.0f}" fill="{DIM_COLOR}">{escape_xml(TITLE)}</text>',
    ]

    for i, (key, val) in enumerate(CONTENT):
        y = TITLE_H + 26 + i * ROW_H
        key_txt = f'{key}'

        # Safety net: if a value is edited later and runs too long, truncate with
        # an ellipsis instead of silently overflowing the card's right edge.
        if len(val) > MAX_VALUE_CHARS:
            print(f'WARNING: "{key}" value is {len(val)} chars (max {MAX_VALUE_CHARS}) - truncated. '
                  f'Shorten this line in CONTENT.')
            val = val[: MAX_VALUE_CHARS - 1].rstrip() + "…"

        val_txt = escape_xml(val)
        row_content = (
            f'<text x="{PAD_X}" y="{y}" fill="{KEY_COLOR}">{escape_xml(key_txt)}</text>'
            f'<text x="{PAD_X + VALUE_X_OFFSET}" y="{y}" fill="{VAL_COLOR}">{val_txt}</text>'
        )

        if static:
            parts.append(row_content)
            continue

        begin = i * FADE_STAGGER_S
        parts.append(
            f'<g opacity="0" transform="translate(-8,0)">'
            f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.2f}s" '
            f'dur="{FADE_DUR_S}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'from="-8,0" to="0,0" begin="{begin:.2f}s" dur="{FADE_DUR_S}s" fill="freeze"/>'
            f'{row_content}'
            f'</g>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    static = os.environ.get("STATIC") == "1"
    svg = render_svg(static=static)
    Path("info-card.svg").write_text(svg, encoding="utf-8")
    print(f"Wrote info-card.svg ({'static preview' if static else 'animated'})")


if __name__ == "__main__":
    main()

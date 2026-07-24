"""
Hero wordmark: renders a name as large ASCII block letters (figlet) into a
self-typing SVG. STATIC CONTENT - never goes stale (no counts/stats baked in).

Usage: python scripts/make_name_svg.py [font]
Env:   STATIC=1  -> frozen preview (no animation)
Output: name-banner.svg (repo root)
"""
import os
import sys
from pathlib import Path

import pyfiglet

NAME = "ANUJ OJHA"
SUBTITLE = "AI-native product builder"
FONT = sys.argv[1] if len(sys.argv) > 1 else "ansi_shadow"

CELL_W = 8.6
CELL_H = 15.0
FONT_SIZE = 15
SUB_SIZE = 15
FILL = "#39d353"
SUB_FILL = "#8b949e"
BG = "#0d1117"
PROMPT_FILL = "#39d353"

COL_STAGGER_S = 0.006   # left-to-right reveal speed
REVEAL_DUR_S = 0.25


def escape_xml(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))


def build() -> str:
    art = pyfiglet.figlet_format(NAME, font=FONT).rstrip("\n")
    lines = [ln.rstrip() for ln in art.split("\n")]
    lines = [ln for ln in lines if ln.strip()]  # drop blank rows

    max_cols = max(len(ln) for ln in lines)
    art_w = max_cols * CELL_W
    art_h = len(lines) * CELL_H

    prompt = "anuj@github:~$ whoami"
    top_pad = 26
    sub_pad = 30
    width = max(art_w, len(prompt) * (FONT_SIZE * 0.62)) + 40
    height = top_pad + art_h + sub_pad + 30

    static = os.environ.get("STATIC") == "1"

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" '
        f'width="{width:.0f}" height="{height:.0f}">',
        f'<rect width="100%" height="100%" fill="{BG}"/>',
        f'<style>text{{font-family:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace;'
        f'white-space:pre;}}</style>',
        # prompt line
        f'<text x="20" y="18" font-size="13" fill="{PROMPT_FILL}">{escape_xml(prompt)}</text>',
    ]

    # ASCII art rows, each column-wiped left to right
    x0 = 20
    for i, line in enumerate(lines):
        y = top_pad + (i + 1) * CELL_H
        safe = escape_xml(line)
        if static:
            parts.append(f'<text x="{x0}" y="{y:.0f}" font-size="{FONT_SIZE}" fill="{FILL}" '
                         f'xml:space="preserve">{safe}</text>')
            continue
        clip_id = f"nc{i}"
        parts.append(
            f'<clipPath id="{clip_id}"><rect x="{x0}" y="{top_pad + i * CELL_H:.0f}" width="0" '
            f'height="{CELL_H:.0f}"><animate attributeName="width" from="0" to="{art_w:.0f}" '
            f'begin="0.3s" dur="0.7s" fill="freeze" calcMode="spline" keySplines="0.2 0 0.2 1"/>'
            f'</rect></clipPath>'
            f'<g clip-path="url(#{clip_id})"><text x="{x0}" y="{y:.0f}" font-size="{FONT_SIZE}" '
            f'fill="{FILL}" xml:space="preserve">{safe}</text></g>'
        )

    # subtitle, fades in after the name lands
    sub_y = top_pad + art_h + sub_pad
    sub_txt = escape_xml(f"> {SUBTITLE}")
    if static:
        parts.append(f'<text x="20" y="{sub_y:.0f}" font-size="{SUB_SIZE}" fill="{SUB_FILL}">{sub_txt}</text>')
    else:
        parts.append(
            f'<text x="20" y="{sub_y:.0f}" font-size="{SUB_SIZE}" fill="{SUB_FILL}" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" begin="1.1s" dur="0.5s" fill="freeze"/>'
            f'{sub_txt}</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    Path("name-banner.svg").write_text(build(), encoding="utf-8")
    print(f"Wrote name-banner.svg (font={FONT}, {'static' if os.environ.get('STATIC') == '1' else 'animated'})")


if __name__ == "__main__":
    main()

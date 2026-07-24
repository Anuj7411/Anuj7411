"""
Renders every profile content section as a styled terminal-window SVG panel,
so the GitHub profile is ALL visuals - no raw markdown text. Self-contained
SMIL animation (GitHub strips JS/CSS).

Edit the SECTIONS data below to change content, then:
    python scripts/make_panels.py
Env: STATIC=1  -> frozen preview (no animation)
Outputs: panel-about.svg, panel-projects.svg, panel-opensource.svg,
         panel-resume.svg, panel-stack.svg  (repo root)
"""
import os
from pathlib import Path

# ---- theme ----
W = 820
PAD = 28
TITLE_H = 40
FONT = 14
CHAR_W = FONT * 0.60
LINE_H = 22
PARA_H = 21
BG = "#0d1117"
BORDER = "#30363d"
TITLEBAR = "#161b22"
GREEN = "#39d353"
CYAN = "#56d4dd"
BODY = "#c9d1d9"
DIM = "#8b949e"
MAXCH = int((W - 2 * PAD) / CHAR_W)

STATIC = os.environ.get("STATIC") == "1"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def wrap(text: str, max_chars: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) <= max_chars:
            cur = f"{cur} {w}".strip()
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


class Panel:
    """Accumulates rendered <text> lines, tracking y; wraps blocks in fade groups."""

    def __init__(self, prompt: str):
        self.prompt = prompt
        self.body = []           # list of (svg_fragment)
        self.y = TITLE_H + 30
        self.block_idx = 0

    def _emit(self, fragments: list[str]):
        # group each block so it fades in as a unit, staggered
        if STATIC:
            self.body.append("".join(fragments))
        else:
            begin = 0.15 + self.block_idx * 0.12
            self.body.append(
                f'<g opacity="0" transform="translate(-6,0)">'
                f'<animate attributeName="opacity" to="1" begin="{begin:.2f}s" dur="0.45s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" from="-6,0" to="0,0" '
                f'begin="{begin:.2f}s" dur="0.45s" fill="freeze"/>'
                f'{"".join(fragments)}</g>'
            )
        self.block_idx += 1

    def para(self, text: str, color: str = BODY, indent: int = 0):
        frags = []
        for ln in wrap(text, MAXCH - int(indent / CHAR_W)):
            self.y += PARA_H
            frags.append(f'<text x="{PAD + indent}" y="{self.y}" fill="{color}">{esc(ln)}</text>')
        self._emit(frags)

    def item(self, head: str, sub: str, body: str):
        frags = []
        self.y += LINE_H + 6
        frags.append(
            f'<text x="{PAD}" y="{self.y}" fill="{GREEN}" font-weight="700">{esc(head)}'
            f'<tspan fill="{DIM}" font-weight="400">  {esc(sub)}</tspan></text>'
        )
        for ln in wrap(body, MAXCH):
            self.y += PARA_H
            frags.append(f'<text x="{PAD}" y="{self.y}" fill="{BODY}">{esc(ln)}</text>')
        self._emit(frags)

    def kv(self, key: str, val: str):
        frags = []
        self.y += LINE_H + 2
        keyw = int(len(key) * CHAR_W) + 16
        first = True
        for ln in wrap(val, MAXCH - int(keyw / CHAR_W)):
            if first:
                frags.append(
                    f'<text x="{PAD}" y="{self.y}" fill="{GREEN}">{esc(key)}'
                    f'<tspan x="{PAD + keyw}" fill="{BODY}">{esc(ln)}</tspan></text>'
                )
                first = False
            else:
                self.y += PARA_H
                frags.append(f'<text x="{PAD + keyw}" y="{self.y}" fill="{BODY}">{esc(ln)}</text>')
        self._emit(frags)

    def gap(self, px: int = 10):
        self.y += px

    def svg(self) -> str:
        height = self.y + PAD
        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" width="{W}" height="{height}">',
            f'<style>text{{font-family:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace;'
            f'font-size:{FONT}px;white-space:pre;}}</style>',
            f'<rect x="0.5" y="0.5" width="{W-1}" height="{height-1}" rx="10" fill="{BG}" stroke="{BORDER}"/>',
            f'<path d="M0.5 10.5 A10 10 0 0 1 10.5 0.5 H{W-10.5} A10 10 0 0 1 {W-0.5} 10.5 V{TITLE_H} H0.5 Z" fill="{TITLEBAR}"/>',
            f'<circle cx="24" cy="{TITLE_H//2}" r="6" fill="#ff5f56"/>',
            f'<circle cx="46" cy="{TITLE_H//2}" r="6" fill="#ffbd2e"/>',
            f'<circle cx="68" cy="{TITLE_H//2}" r="6" fill="#27c93f"/>',
            f'<text x="94" y="{TITLE_H//2 + 5}" fill="{DIM}">anuj@github:~$ {esc(self.prompt)}</text>',
        ]
        parts.extend(self.body)
        parts.append("</svg>")
        return "\n".join(parts)


def build():
    panels = {}

    # ABOUT
    p = Panel("cat about.md")
    p.para("AI-native product builder. I find problems in the tools I use, build the fix, "
           "ship it, and measure it. I ship at volume solo by orchestrating a pipeline of "
           "AI coding agents (Claude Code, Codex) across the whole dev lifecycle.")
    p.gap(8)
    p.para("Open to joining an early-stage AI team as a founding-track builder or technical "
           "product manager, remote.", color=DIM)
    panels["panel-about.svg"] = p.svg()

    # PROJECTS
    p = Panel("ls projects/")
    p.item("Sipcode", "AI coding-agent tooling",
           "MCP server that cuts AI coding-agent token use by a 62.6% median on a locked "
           "benchmark. On the Official MCP Registry; #12 of 1,086 on Product Hunt.")
    p.item("AnswerFox", "AI-readiness platform",
           "Audits how AI crawlers actually read a site, then ships the fixes as GitHub PRs "
           "and re-audits on merge. Built on RSC, Drizzle/Supabase (RLS), Inngest, Cloudflare.")
    p.item("Judix", "agent evals infrastructure",
           "Real-time evals for AI agents and RAG. A Rust core scores every step live at ~$0 "
           "(deterministic rules plus a model judge). Streaming API, CLI, LangChain / CrewAI / Codex hooks.")
    p.item("Sotto", "consumer web app",
           "Anonymous Secret Santa, shipped solo in 14 days and launched on Product Hunt. "
           "Privacy enforced at the database layer (Sattolo shuffle + bcrypt + RLS), not as a toggle.")
    panels["panel-projects.svg"] = p.svg()

    # OPEN SOURCE
    p = Panel("./open-source.sh")
    p.para("Pull requests merged across five LLM-observability platforms -- Comet Opik, "
           "BerriAI LiteLLM, and more -- fixing 2x-16x billing bugs on flagship models and "
           "recovering 500+ dropped model entries. Every fix ships with a regression test.")
    p.gap(8)
    p.para("Publicly thanked and invited back by the Opik lead maintainer, with more PRs in "
           "review across Arize Phoenix, Langfuse, and Helicone.", color=DIM)
    panels["panel-opensource.svg"] = p.svg()

    # RESUME (experience + education)
    p = Panel("cat resume.md")
    p.item("Data Scientist Intern", "Hackveda Solutions (Remote)",
           "Shipped ML pipelines end-to-end under sprint deadlines; selected models by "
           "benchmarking on accuracy, precision, recall, and F1, and turned output into "
           "decisions non-technical stakeholders could act on.")
    p.gap(6)
    p.item("B.Tech, CS & Business Systems", "OIST Bhopal -- CGPA 8.09/10",
           "IEEE-published (WardROBO, CODE 2K-26).")
    p.kv("certs", "Claude Code in Action & Intro to MCP (Anthropic) . McKinsey Forward . "
                  "OCI Generative AI Professional (Oracle) . Technical Product Management (LinkedIn)")
    panels["panel-resume.svg"] = p.svg()

    # STACK
    p = Panel("cat stack.txt")
    p.kv("languages", "TypeScript . Python . Rust . Java . SQL")
    p.kv("ai-tooling", "Claude Code . Codex . MCP . evals & LLM observability (Opik, LiteLLM, "
                       "Phoenix, Langfuse) . RAG . OpenAI / Gemini / Anthropic APIs . OpenTelemetry")
    p.kv("infra", "Next.js . React . Node.js . Supabase / PostgreSQL (RLS) . Drizzle . Inngest . "
                  "Cloudflare . Docker . GitHub Actions")
    panels["panel-stack.svg"] = p.svg()

    return panels


def main():
    for name, svg in build().items():
        Path(name).write_text(svg, encoding="utf-8")
        print(f"Wrote {name}")


if __name__ == "__main__":
    main()

"""
Build a neofetch-style info card SVG (Andrew6rant style) to sit to the RIGHT of
the ASCII portrait: colored key/value rows for work experience, tech stack, and
highlights -- NOT GitHub stats (the contribution graph covers those).

Static content, hand-authored below. Lines fade/slide in on a short stagger so
it feels like the panel is printing alongside the portrait. STATIC=1 emits the
frozen state for Quick Look previews.
"""
import html
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "info-card.svg")
STATIC = bool(os.environ.get("STATIC"))

W, H = 480, 400
PAD = 20
TITLEBAR_H = 30
KEY_X = PAD
VAL_X = PAD + 92
LINE_H = 23.5

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#e6edf3"
KEY = "#ffa657"      # orange keys
SECTION = "#58a6ff"  # blue section headers
GREEN = "#3fb950"
ACCENT = "#22d3ee"   # cyan accent

ROWS = [
    ("host",),
    ("kv", "Focus", "Modern & responsive web apps"),
    ("kv", "Style", "Clean code, smooth interactions"),
    ("kv", "Motto", "Always learning, always building"),
    ("gap",),
    ("sec", "Stack"),
    ("kv", "Lang", "JS, TS, Python, Java, C, PHP"),
    ("kv", "Frontend", "HTML5, Vite, Figma, Canva"),
    ("kv", "Backend", "Node.js, NPM, Firebase, Vercel"),
    ("kv", "DB", "MySQL, Postgres, MongoDB, SQLite"),
    ("kv", "BaaS", "Supabase, Appwrite, Firebase"),
    ("gap",),
    ("sec", "Highlights"),
    ("bul", "Passionate full-stack developer"),
    ("bul", "Engaging digital experiences"),
]


def esc(s):
    return html.escape(s)


def rise(inner, i):
    """fade + slight upward slide, staggered by row index; freezes visible."""
    if STATIC:
        return f"<g>{inner}</g>"
    delay = 0.15 + i * 0.06
    return (f'<g opacity="0" transform="translate(0,5)">{inner}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" '
            f'begin="{delay:.2f}s" dur="0.4s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/></g>')


parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
    '<defs>'
    f'<linearGradient id="ibg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient>'
    f'<linearGradient id="lineGrad" x1="0" y1="0" x2="1" y2="0">'
    f'<stop offset="0" stop-color="{SECTION}" stop-opacity="0.8"/>'
    f'<stop offset="1" stop-color="{FRAME}" stop-opacity="0.1"/></linearGradient>'
    f'<linearGradient id="hostGrad" x1="0" y1="0" x2="1" y2="0">'
    f'<stop offset="0" stop-color="{GREEN}" stop-opacity="0.8"/>'
    f'<stop offset="1" stop-color="{FRAME}" stop-opacity="0.1"/></linearGradient>'
    '</defs>',
    f'<rect width="{W}" height="{H}" rx="12" fill="url(#ibg)"/>',
    f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/>',
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
]
for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
parts.append(f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
             f'text-anchor="middle">virendra@github: ~$ neofetch</text>')

y = TITLEBAR_H + 34
for i, row in enumerate(ROWS):
    kind = row[0]
    if kind == "gap":
        y += LINE_H * 0.4
        continue
    if kind == "host":
        inner = (f'<text x="{KEY_X}" y="{y:.1f}" font-size="14.5" font-weight="700">'
                 f'<tspan fill="{GREEN}">virendra</tspan><tspan fill="{MUTED}">@</tspan>'
                 f'<tspan fill="{ACCENT}">github</tspan></text>'
                 f'<rect x="{KEY_X+142}" y="{y-4:.1f}" width="{W-PAD-(KEY_X+142)}" height="1.5" fill="url(#hostGrad)"/>')
    elif kind == "sec":
        title = esc(row[1])
        inner = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{SECTION}" font-size="13" font-weight="700">'
                 f'{title}</text>'
                 f'<rect x="{KEY_X + len(row[1])*8.5 + 8}" y="{y-4:.1f}" width="{W-PAD-(KEY_X + len(row[1])*8.5 + 8)}" height="1.5" fill="url(#lineGrad)"/>')
    elif kind == "kv":
        key, val = esc(row[1]), esc(row[2])
        if key in ["Lang", "Frontend", "Backend", "DB", "BaaS"]:
            inner_parts = [f'<text x="{KEY_X}" y="{y:.1f}" fill="{KEY}" font-size="12.5" font-weight="700">{key}</text>']
            current_x = VAL_X
            for tag in val.split(","):
                tag = tag.strip()
                tag_w = len(tag) * 7.5 + 14  
                inner_parts.append(f'<rect x="{current_x}" y="{y-12}" width="{tag_w}" height="18" rx="4" fill="#161b22" stroke="{SECTION}" stroke-opacity="0.3"/>')
                inner_parts.append(f'<text x="{current_x+7}" y="{y+1:.1f}" fill="{INK}" font-size="11.5">{tag}</text>')
                current_x += tag_w + 6
            inner = "".join(inner_parts)
        else:
            inner = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{KEY}" font-size="12.5" font-weight="700">{key}</text>'
                     f'<text x="{VAL_X}" y="{y:.1f}" fill="{INK}" font-size="12.5">{val}</text>')
    elif kind == "bul":
        txt = esc(row[1])
        chevron = f'<path d="M {KEY_X+2} {y-9} L {KEY_X+7} {y-4} L {KEY_X+2} {y+1}" stroke="{ACCENT}" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        inner = (chevron + f'<text x="{KEY_X+16}" y="{y:.1f}" fill="{INK}" font-size="12.5">{txt}</text>')
    else:
        continue
    parts.append(rise(inner, i))
    y += LINE_H

parts.append("</svg>")
svg = "".join(parts)
with open(OUT, "w") as f:
    f.write(svg)
print("wrote", OUT, len(svg), "bytes;", W, "x", H, "content_bottom", round(y))


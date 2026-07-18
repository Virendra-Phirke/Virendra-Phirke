#!/usr/bin/env python3
"""
Generate a Most Used Languages SVG card in a terminal UI style with an animated pie chart.
Fetches real data from the GitHub API (no auth needed for public profiles).
Usage: python make_lang_card.py [username] [output.svg]
"""
import sys, json, os, urllib.request, html, math

USER = sys.argv[1] if len(sys.argv) > 1 else "virendra-phirke"
OUT  = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lang-card.svg")

def api(url):
    req = urllib.request.Request(url, headers={"User-Agent": "stats-card/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())

def get_languages(user):
    """Aggregate language bytes across all repos."""
    repos = []
    page = 1
    while True:
        batch = api(f"https://api.github.com/users/{user}/repos?per_page=100&page={page}")
        if not batch:
            break
        repos.extend(batch)
        page += 1

    lang_totals = {}
    for r in repos:
        if r.get("fork"):
            continue
        try:
            langs = api(r["languages_url"])
            for lang, bytes_count in langs.items():
                lang_totals[lang] = lang_totals.get(lang, 0) + bytes_count
        except Exception:
            pass

    total_bytes = sum(lang_totals.values()) or 1
    sorted_langs = sorted(lang_totals.items(), key=lambda x: -x[1])[:6]

    return [(name, round(b / total_bytes * 100, 1)) for name, b in sorted_langs]

# ---- SVG rendering ----

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
GRAY = "#7d8590"
TEXT = "#c9d1d9"

LANG_COLORS = {
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "Python": "#3572a5",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "Java": "#b07219",
    "C": "#555555",
    "PHP": "#4f5d95",
    "Shell": "#89e051",
    "Ruby": "#701516",
    "Go": "#00add8",
    "Rust": "#dea584",
    "C++": "#f34b7d",
    "C#": "#178600",
    "Kotlin": "#A97BFF",
    "Swift": "#F05138",
    "Dart": "#00B4AB",
    "Vue": "#41b883",
    "SCSS": "#c6538c",
    "Svelte": "#ff3e00",
}

TITLEBAR_H = 30
PAD = 20
CARD_W = 460
CARD_H = 245
TOTAL_W = CARD_W
TOTAL_H = CARD_H

def rise(inner, delay):
    return (
        f'<g opacity="0" transform="translate(0,5)">{inner}'
        f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.45s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" '
        f'begin="{delay:.2f}s" dur="0.45s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/></g>'
    )

def render_lang_card(languages):
    """Render the Most Used Languages card with an animated donut chart."""
    parts = []
    # Card background
    parts.append(f'<rect x="0" y="0" width="{CARD_W}" height="{CARD_H}" rx="12" fill="url(#sbg)"/>')
    parts.append(f'<rect x="0.5" y="0.5" width="{CARD_W-1}" height="{CARD_H-1}" rx="12" fill="none" stroke="{FRAME}"/>')
    parts.append(f'<line x1="0" y1="{TITLEBAR_H}" x2="{CARD_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>')

    # Title bar dots
    for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{PAD+i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')

    # Title
    parts.append(f'<text x="{CARD_W/2}" y="{TITLEBAR_H/2+4}" fill="{GRAY}" font-size="11" text-anchor="middle">Most Used Languages</text>')

    # Pie chart variables
    R = 60
    C = 2 * math.pi * R
    cx = 120
    cy = TITLEBAR_H + 105
    
    cumulative_pct = 0
    pie_parts = []
    label_parts = []
    
    # Background ring for the donut
    pie_parts.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="transparent" stroke="{FRAME}" stroke-width="30" opacity="0.4"/>')
    
    label_x = 250
    label_y = TITLEBAR_H + 40
    
    for idx, (lang, pct) in enumerate(languages):
        color = LANG_COLORS.get(lang, "#8b8b8b")
        dash_length = (pct / 100.0) * C
        dash_offset = C - (cumulative_pct / 100.0) * C
        
        delay = 0.3 + idx * 0.15
        
        # Donut segment
        slice_inner = (
            f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="transparent" stroke="{color}" stroke-width="30" '
            f'stroke-dasharray="0 {C}" stroke-dashoffset="{dash_offset}" transform="rotate(-90 {cx} {cy})">'
            f'<animate attributeName="stroke-dasharray" from="0 {C}" to="{dash_length} {C}" '
            f'begin="{delay:.2f}s" dur="0.8s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/>'
            f'</circle>'
        )
        pie_parts.append(slice_inner)
        
        # Label on the right
        label_inner = (
            f'<circle cx="{label_x}" cy="{label_y-4}" r="5" fill="{color}"/>'
            f'<text x="{label_x + 15}" y="{label_y}" fill="{color}" font-size="13" font-weight="700">{html.escape(lang)}</text>'
            f'<text x="{CARD_W-PAD}" y="{label_y}" fill="{TEXT}" font-size="13" font-weight="600" text-anchor="end">{pct}%</text>'
        )
        label_parts.append(rise(label_inner, delay))
        
        cumulative_pct += pct
        label_y += 30

    return "\n".join(parts + pie_parts + label_parts)

def build_svg(languages):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{TOTAL_W}" height="{TOTAL_H}" viewBox="0 0 {TOTAL_W} {TOTAL_H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
<defs>
  <linearGradient id="sbg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>
  </linearGradient>
</defs>
{render_lang_card(languages)}
</svg>'''
    return svg

if __name__ == "__main__":
    print("Fetching language stats...")
    languages = get_languages(USER)
    for lang, pct in languages:
        print(f"  {lang}: {pct}%")

    svg = build_svg(languages)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {OUT} ({len(svg)} bytes)")

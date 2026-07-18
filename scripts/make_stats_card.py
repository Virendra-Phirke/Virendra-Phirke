#!/usr/bin/env python3
"""
Generate a GitHub Stats + Most Used Languages SVG card in a terminal UI style.
Fetches real data from the GitHub API (no auth needed for public profiles).
Usage: python make_stats_card.py [username] [output.svg]
"""
import sys, json, os, urllib.request, html

USER = sys.argv[1] if len(sys.argv) > 1 else "virendra-phirke"
OUT  = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "stats-card.svg")

# ---- GitHub API helpers ----

def api(url):
    req = urllib.request.Request(url, headers={"User-Agent": "stats-card/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def get_user_stats(user):
    """Fetch stars, commits (events proxy), PRs, issues from the public API."""
    profile = api(f"https://api.github.com/users/{user}")

    # total stars across all repos
    repos = []
    page = 1
    while True:
        batch = api(f"https://api.github.com/users/{user}/repos?per_page=100&page={page}")
        if not batch:
            break
        repos.extend(batch)
        page += 1

    total_stars = sum(r.get("stargazers_count", 0) for r in repos)

    # commits this year from events (best effort, public API)
    events = api(f"https://api.github.com/users/{user}/events/public?per_page=100")
    push_commits = sum(
        len(e.get("payload", {}).get("commits", []))
        for e in events if e.get("type") == "PushEvent"
    )

    # search for PRs and issues
    try:
        pr_data = api(f"https://api.github.com/search/issues?q=author:{user}+type:pr&per_page=1")
        total_prs = pr_data.get("total_count", 0)
    except Exception:
        total_prs = 0

    try:
        issue_data = api(f"https://api.github.com/search/issues?q=author:{user}+type:issue&per_page=1")
        total_issues = issue_data.get("total_count", 0)
    except Exception:
        total_issues = 0

    return {
        "name": profile.get("name", user),
        "stars": total_stars,
        "commits": push_commits,
        "prs": total_prs,
        "issues": total_issues,
        "public_repos": profile.get("public_repos", 0),
    }


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

# colors
BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
GRAY = "#7d8590"
TEXT = "#c9d1d9"
GREEN = "#3fb950"
CYAN = "#22d3ee"
YELLOW = "#ffbd2e"

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

STAT_ICONS = {
    "stars": ("⭐", YELLOW),
    "commits": ("◉", GREEN),
    "prs": ("🔀", CYAN),
    "issues": ("⊙", "#f85149"),
}

TITLEBAR_H = 30
PAD = 20
CARD_W = 460
CARD_H = 245
TOTAL_W = CARD_W * 2 + 30
TOTAL_H = CARD_H


def rise(inner, delay):
    return (
        f'<g opacity="0" transform="translate(0,5)">{inner}'
        f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.45s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" '
        f'begin="{delay:.2f}s" dur="0.45s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/></g>'
    )


def render_stats_card(stats, x_off):
    """Render the left GitHub Stats card."""
    parts = []
    # Card background
    parts.append(f'<rect x="{x_off}" y="0" width="{CARD_W}" height="{CARD_H}" rx="12" fill="url(#sbg)"/>')
    parts.append(f'<rect x="{x_off+0.5}" y="0.5" width="{CARD_W-1}" height="{CARD_H-1}" rx="12" fill="none" stroke="{FRAME}"/>')
    parts.append(f'<line x1="{x_off}" y1="{TITLEBAR_H}" x2="{x_off+CARD_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>')

    # Title bar dots
    for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{x_off+PAD+i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')

    # Title
    name = html.escape(stats["name"])
    title = f"{name}'s GitHub Stats"
    parts.append(f'<text x="{x_off+CARD_W/2}" y="{TITLEBAR_H/2+4}" fill="{GRAY}" font-size="11" text-anchor="middle">{title}</text>')

    # Stats rows
    stat_rows = [
        ("Total Stars Earned", stats["stars"], "stars"),
        (f"Total Commits ({__import__('datetime').datetime.now().year})", stats["commits"], "commits"),
        ("Total PRs", stats["prs"], "prs"),
        ("Total Issues", stats["issues"], "issues"),
    ]

    y = TITLEBAR_H + 42
    for idx, (label, value, key) in enumerate(stat_rows):
        icon_char, icon_color = STAT_ICONS[key]
        delay = 0.2 + idx * 0.12

        row_inner = (
            f'<text x="{x_off+PAD}" y="{y}" font-size="13">'
            f'<tspan fill="{icon_color}" font-size="14">{icon_char}</tspan>'
            f'  <tspan fill="{TEXT}">{html.escape(label)}</tspan></text>'
            f'<text x="{x_off+CARD_W-PAD}" y="{y}" fill="{TEXT}" font-size="14" font-weight="700" text-anchor="end">{value:,}</text>'
        )
        parts.append(rise(row_inner, delay))
        y += 40

    return "\n".join(parts)


def render_lang_card(languages, x_off):
    """Render the right Most Used Languages card."""
    parts = []
    # Card background
    parts.append(f'<rect x="{x_off}" y="0" width="{CARD_W}" height="{CARD_H}" rx="12" fill="url(#sbg)"/>')
    parts.append(f'<rect x="{x_off+0.5}" y="0.5" width="{CARD_W-1}" height="{CARD_H-1}" rx="12" fill="none" stroke="{FRAME}"/>')
    parts.append(f'<line x1="{x_off}" y1="{TITLEBAR_H}" x2="{x_off+CARD_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>')

    # Title bar dots
    for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{x_off+PAD+i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')

    # Title
    parts.append(f'<text x="{x_off+CARD_W/2}" y="{TITLEBAR_H/2+4}" fill="{GRAY}" font-size="11" text-anchor="middle">Most Used Languages</text>')

    # Language bars
    bar_left = x_off + PAD
    bar_w = CARD_W - PAD * 2 - 60  # leave room for percentage
    y = TITLEBAR_H + 38

    for idx, (lang, pct) in enumerate(languages):
        delay = 0.3 + idx * 0.12
        color = LANG_COLORS.get(lang, "#8b8b8b")
        filled_w = max(4, bar_w * pct / 100)

        row_inner = (
            # Language name
            f'<text x="{bar_left}" y="{y}" fill="{color}" font-size="12" font-weight="700">{html.escape(lang)}</text>'
            # Percentage
            f'<text x="{x_off+CARD_W-PAD}" y="{y}" fill="{TEXT}" font-size="12" font-weight="600" text-anchor="end">{pct}%</text>'
            # Bar background
            f'<rect x="{bar_left}" y="{y+5}" width="{bar_w}" height="7" rx="3.5" fill="{GRAY}" opacity="0.25"/>'
            # Bar filled
            f'<rect x="{bar_left}" y="{y+5}" width="{filled_w}" height="7" rx="3.5" fill="{color}"/>'
        )
        parts.append(rise(row_inner, delay))
        y += 33

    return "\n".join(parts)


def build_svg(stats, languages):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{TOTAL_W}" height="{TOTAL_H}" viewBox="0 0 {TOTAL_W} {TOTAL_H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
<defs>
  <linearGradient id="sbg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>
  </linearGradient>
</defs>
{render_stats_card(stats, 0)}
{render_lang_card(languages, CARD_W + 30)}
</svg>'''
    return svg


if __name__ == "__main__":
    print(f"Fetching GitHub stats for {USER}...")
    stats = get_user_stats(USER)
    print(f"  Stars: {stats['stars']}, Commits: {stats['commits']}, PRs: {stats['prs']}, Issues: {stats['issues']}")

    print("Fetching language stats...")
    languages = get_languages(USER)
    for lang, pct in languages:
        print(f"  {lang}: {pct}%")

    svg = build_svg(stats, languages)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {OUT} ({len(svg)} bytes)")

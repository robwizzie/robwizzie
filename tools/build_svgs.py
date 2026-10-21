"""Builds the animated header used in the profile README.

Run from the repo root:  python3 tools/build_svgs.py
A GitHub Action reruns it every few hours so the live numbers stay current.
"""
import json
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
FONT = "'Segoe UI', -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"



# Flamey, matching the Mile A Day app's mascot (FlameBuddyFigure.swift).
# Drawn in a 1200 x 1240 box; the body spans x 185-1012, y 22-1175.
FLAMEY_DEFS = """
  <linearGradient id="fl-outer" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffef4a"/><stop offset="0.5" stop-color="#ff9500"/><stop offset="1" stop-color="#ff3a1a"/>
  </linearGradient>
  <linearGradient id="fl-inner" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffe95a"/><stop offset="1" stop-color="#ff9a26"/>
  </linearGradient>
  <clipPath id="fl-mouth"><path d="M438 905 Q600 990 760 905 C 745 1075, 455 1075, 438 905 Z"/></clipPath>"""

FLAMEY_OUTER = ("M600 22 C 700 120, 805 190, 810 305 C 813 350, 800 390, 785 418 C 840 570, 1012 680, 1012 870 "
                "C 1012 1080, 860 1175, 600 1175 C 340 1175, 185 1080, 185 860 C 185 790, 220 740, 285 672 "
                "C 265 590, 270 520, 300 500 C 320 470, 350 475, 382 503 C 375 300, 440 150, 600 22 Z")
FLAMEY_INNER = ("M612 420 C 660 500, 760 560, 665 672 C 668 710, 690 740, 715 765 L 808 900 "
                "C 808 1030, 710 1090, 600 1090 C 490 1090, 392 1030, 392 900 L 482 745 C 515 640, 515 520, 612 420 Z")


def flamey(mode="stand", tempo=0.45):
    """mode "stand": bob and blink. mode "run": legs and arms swing too."""
    blink = 'keyTimes="0;0.9;0.93;0.96;1" dur="4s" repeatCount="indefinite"'
    face = f"""
  <ellipse cx="426" cy="808" rx="72" ry="93" fill="#33120a"><animate attributeName="ry" values="93;93;8;93;93" {blink}/></ellipse>
  <ellipse cx="774" cy="808" rx="72" ry="93" fill="#33120a"><animate attributeName="ry" values="93;93;8;93;93" {blink}/></ellipse>
  <circle cx="404" cy="772" r="21" fill="#fff"><animate attributeName="opacity" values="1;1;0;1;1" {blink}/></circle>
  <circle cx="752" cy="772" r="21" fill="#fff"><animate attributeName="opacity" values="1;1;0;1;1" {blink}/></circle>
  <path d="M438 905 Q600 990 760 905 C 745 1075, 455 1075, 438 905 Z" fill="#3d0a0a"/>
  <rect x="533" y="992" width="134" height="64" rx="28" fill="#ff6b5a" clip-path="url(#fl-mouth)"/>"""
    limbs_back = limbs_front = ""
    if mode == "run":
        def swing(cx, cy, a):
            return (f'<animateTransform attributeName="transform" type="rotate" dur="{tempo}s" repeatCount="indefinite" '
                    f'values="{a} {cx} {cy};{-a} {cx} {cy};{a} {cx} {cy}"/>')
        leg = lambda cx, a: (f'<g><rect x="{cx - 45}" y="1090" width="90" height="190" rx="45" fill="#ff4a1c"/>'
                             f'<ellipse cx="{cx + 20}" cy="1275" rx="75" ry="34" fill="#e8380f"/>{swing(cx, 1110, a)}</g>')
        arm = lambda cx, cy, a: (f'<g><rect x="{cx - 34}" y="{cy}" width="68" height="200" rx="34" fill="#ff7a12"/>'
                                 f'<circle cx="{cx}" cy="{cy + 200}" r="44" fill="#ff8f1f"/>{swing(cx, cy + 20, a)}</g>')
        limbs_back = leg(470, 30) + leg(730, -30)
        limbs_front = arm(205, 820, -35) + arm(995, 820, 35)
    lean = ' transform="rotate(7 600 700)"' if mode == "run" else ""
    return f"""<g{lean}>
  {limbs_back}
  <path d="{FLAMEY_OUTER}" fill="url(#fl-outer)"/>
  <path d="{FLAMEY_INNER}" fill="url(#fl-inner)"/>{face}
  {limbs_front}
</g>"""


def chip(x, y, text, accent):
    w = round(len(text) * 7.6 + 44)
    return (
        f'<g transform="translate({x} {y})">'
        f'<rect width="{w}" height="34" rx="17" fill="#ffffff" fill-opacity="0.06" stroke="#ffffff" stroke-opacity="0.12"/>'
        f'<circle cx="18" cy="17" r="4" fill="{accent}"/>'
        f'<text x="{(w + 14) / 2:.1f}" y="22" text-anchor="middle" font-family="{FONT}" font-size="15" fill="#e7e1db">{escape(text)}</text></g>',
        w,
    )


def rotating(lines, x, y, size, color, each=4.0):
    """Lines fade in and out one at a time, forever."""
    total = each * len(lines)
    out = []
    for i, text in enumerate(lines):
        a, b = i / len(lines), (i + 1) / len(lines)
        f = 0.35 / total  # fade duration as a fraction of the loop
        if i == 0:
            kt, vals = f"0;{b - f:.4f};{b:.4f};{1 - f:.4f};1", "1;1;0;0;1"
        else:
            kt, vals = f"0;{a:.4f};{a + f:.4f};{b - f:.4f};{b:.4f};1", "0;0;1;1;0;0"
        out.append(
            f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="{color}" opacity="{1 if i == 0 else 0}">{escape(text)}'
            f'<animate attributeName="opacity" dur="{total}s" repeatCount="indefinite" keyTimes="{kt}" values="{vals}"/></text>'
        )
    return "\n".join(out)


UA = {"User-Agent": "Mozilla/5.0 (compatible; robwizzie-profile/1.0; +https://github.com/robwizzie)", "Accept": "application/json"}


def get_json(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=15) as r:
        return json.load(r)


def fetch_live():
    """Live numbers for the header. Falls back to the last saved values if a source is down."""
    cache_path = ASSETS / "live.json"
    try:
        live = json.loads(cache_path.read_text())
    except Exception:
        live = {}
    try:
        s = get_json("https://mad.mindgoblin.tech/public/stats")
        live["mad"] = {k: s[k] for k in ("total_users", "total_miles", "miles_today")}
    except Exception as e:
        print("Mile A Day stats unavailable, keeping last values:", e)
    try:
        url = "https://raw.githubusercontent.com/robwizzie/top-dogs-pool/main/data/apa.json"
        team = get_json(url)["team"]
        live["dawgs"] = {
            "wins": team["record"]["wins"],
            "losses": team["record"]["losses"],
            "rank": team.get("divisionRank"),
            "session": team.get("session"),
        }
    except Exception as e:
        print("Top Dawgs data unavailable, keeping last values:", e)
    cache_path.write_text(json.dumps(live, indent=2) + "\n")
    return live


def header(live):
    W, H = 1200, 360
    omw_w = 44  # running Flamey width at 0.037 scale
    line_y, x0, x1 = 284, 64, W - 64
    run = 14

    chips_svg, x = [], 64
    for text, accent in [("South Jersey", "#7aa2ff"), ("Shipping on the App Store", "#5ccf8a")]:
        svg, w = chip(x, 192, text, accent)
        chips_svg.append(svg)
        x += w + 12

    taglines = [
        "I build apps for my friends, my pool team and anyone who'll run a mile.",
        "By day: the platform behind a test-prep company. By night: side projects.",
        "Currently turning my living room TV into a custom home screen.",
    ]

    mad, dawgs = live.get("mad", {}), live.get("dawgs", {})
    left = []
    if mad:
        left = [
            f"{mad['total_users']:,} people on Mile A Day",
            f"{round(mad['total_miles']):,} miles logged",
            f"{mad['miles_today']:g} miles today",
        ]
    right = ""
    if dawgs:
        rank = f" · #{dawgs['rank']} in division" if dawgs.get("rank") else ""
        right = f"Top Dawgs {dawgs['wins']}–{dawgs['losses']}{rank}"

    ticks = "".join(
        f'<rect x="{x0 + (x1 - x0) * k / 4 - 0.75:.1f}" y="{line_y - 5}" width="1.5" height="10" fill="#ffffff" fill-opacity="0.25"/>'
        for k in range(5)
    )
    stats = ""
    if left:
        stats += (
            f'<text x="{x0}" y="{line_y + 40}" font-family="{FONT}" font-size="15" fill="#a39b94">'
            f'<tspan fill="#ff7a45" font-weight="600">● LIVE</tspan>  {escape("  ·  ".join(left))}</text>'
        )
    if right:
        stats += f'<text x="{x1}" y="{line_y + 40}" text-anchor="end" font-family="{FONT}" font-size="15" fill="#a39b94">{escape(right)}</text>'

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Hey, I'm Rob Wiscount: full-stack and iOS developer and co-founder of Mile A Day">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#15141b"/><stop offset="1" stop-color="#2c1217"/>
  </linearGradient>
  <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#ff6a3d" stop-opacity="0.26"/><stop offset="1" stop-color="#ff6a3d" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="trail" x1="0" x2="1">
    <stop offset="0" stop-color="#ff7a45" stop-opacity="0"/><stop offset="1" stop-color="#ff7a45" stop-opacity="0.9"/>
  </linearGradient>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  {FLAMEY_DEFS}
</defs>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <circle cx="1020" cy="130" r="165" fill="url(#glow)"/>
  <g font-family="{FONT}">
    <text x="64" y="90" font-size="50" font-weight="700" fill="#f5f2ee" letter-spacing="-0.5">Hey, I'm Rob</text>
    <text x="66" y="130" font-size="21" fill="#c9c1b9">Full-stack and iOS developer · Co-founder of Mile A Day</text>
  </g>
  {rotating(taglines, 66, 168, 17, "#8f8780")}
  {"".join(chips_svg)}
  <g transform="translate(936 36) scale(0.14)">
    <g><animateTransform attributeName="transform" type="translate" values="0 0;0 -50;0 0" dur="2.4s" repeatCount="indefinite"/>
    {flamey("stand")}</g>
  </g>

  <!-- the mile: Flamey runs it, the trail fills in behind him -->
  <rect x="{x0}" y="{line_y - 1}" width="{x1 - x0}" height="2" rx="1" fill="#ffffff" fill-opacity="0.12"/>
  {ticks}
  <text x="{x1}" y="{line_y - 12}" text-anchor="end" font-family="{MONO}" font-size="12" fill="#ffffff" fill-opacity="0.35">1 MI</text>
  <rect x="{x0}" y="{line_y - 1}" height="2" rx="1" fill="url(#trail)" width="0">
    <animate attributeName="width" values="0;{x1 - x0};{x1 - x0};0" keyTimes="0;0.85;0.97;1" dur="{run}s" repeatCount="indefinite"/>
  </rect>
  <g>
    <animateTransform attributeName="transform" type="translate" values="{x0 - omw_w / 2:.0f} 0;{x1 - omw_w / 2:.0f} 0;{x1 - omw_w / 2:.0f} 0;{x0 - omw_w / 2:.0f} 0" keyTimes="0;0.85;0.97;1" dur="{run}s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="1;1;1;0;1" keyTimes="0;0.85;0.95;0.97;1" dur="{run}s" repeatCount="indefinite"/>
    <g transform="translate(0 {line_y - 48}) scale(0.037)">
      <g><animateTransform attributeName="transform" type="translate" values="0 0;0 -80;0 0" dur="0.225s" repeatCount="indefinite"/>
      {flamey("run")}</g>
    </g>
  </g>
  {stats}
</g>
</svg>"""


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "header.svg").write_text(header(fetch_live()))
    print("header.svg", (ASSETS / "header.svg").stat().st_size // 1024, "KB")

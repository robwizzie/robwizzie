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



# Flamey, as drawn for the Mile A Day merch (shop/components/designs.tsx, FlameyShape).
# 200 x 232 units. Arms and legs are separate so they can move.
COCOA = "#2a1410"
FLAMEY_DEFS = """
  <linearGradient id="flamey-body" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffe25a"/><stop offset="0.45" stop-color="#ff9a2e"/><stop offset="1" stop-color="#ff4b24"/>
  </linearGradient>
  <linearGradient id="flamey-core" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff3a0"/><stop offset="1" stop-color="#ffc24a"/>
  </linearGradient>"""


def flamey(mode="stand", tempo=0.45):
    """mode: "wave" (right arm waves) or "run" (legs and arms swing)."""
    def leg(cx, phase):
        body = (f'<rect x="{cx - 13}" y="176" width="26" height="50" rx="13" fill="#ff5a2a"/>'
                f'<ellipse cx="{cx}" cy="226" rx="20" ry="9" fill="#ff4b24"/>')
        if mode != "run":
            return f"<g>{body}</g>"
        a, b = (-28, 28) if phase else (28, -28)
        return (f'<g>{body}<animateTransform attributeName="transform" type="rotate" dur="{tempo}s" repeatCount="indefinite" '
                f'values="{a} {cx} 180;{b} {cx} 180;{a} {cx} 180"/></g>')

    def arm(side, phase):
        if side == "l":
            path, hand, pivot = "M44 132 C 30 118, 26 100, 30 88", (30, 84), (44, 132)
        else:
            path, hand, pivot = "M156 132 C 170 118, 174 100, 170 88", (170, 84), (156, 132)
        body = (f'<path d="{path}" stroke="#ff7a2a" stroke-width="18" stroke-linecap="round" fill="none"/>'
                f'<circle cx="{hand[0]}" cy="{hand[1]}" r="13" fill="#ff9a3a"/>')
        if mode == "wave" and side == "r":
            anim = (f'<animateTransform attributeName="transform" type="rotate" dur="2.4s" repeatCount="indefinite" '
                    f'keyTimes="0;0.12;0.24;0.36;0.48;1" values="0 {pivot[0]} {pivot[1]};22 {pivot[0]} {pivot[1]};-6 {pivot[0]} {pivot[1]};22 {pivot[0]} {pivot[1]};0 {pivot[0]} {pivot[1]};0 {pivot[0]} {pivot[1]}"/>')
        elif mode == "run":
            a, b = (-20, 20) if phase else (20, -20)
            anim = (f'<animateTransform attributeName="transform" type="rotate" dur="{tempo}s" repeatCount="indefinite" '
                    f'values="{a} {pivot[0]} {pivot[1]};{b} {pivot[0]} {pivot[1]};{a} {pivot[0]} {pivot[1]}"/>')
        else:
            anim = ""
        return f"<g>{body}{anim}</g>"

    lean = ' transform="rotate(8 100 120)"' if mode == "run" else ""
    return f"""<g{lean}>
  {leg(79, 0)}{leg(121, 1)}
  {arm("l", 1)}{arm("r", 0)}
  <path d="M100 6 C 128 40, 168 76, 166 136 C 164 176, 136 194, 100 194 C 64 194, 36 176, 34 136 C 32 104, 46 84, 60 70 C 62 88, 68 98, 76 102 C 72 66, 82 36, 100 6 Z" fill="url(#flamey-body)" stroke="#fff" stroke-opacity="0.35" stroke-width="3"/>
  <path d="M100 66 C 112 86, 124 104, 120 128 C 116 144, 84 144, 80 128 C 76 108, 90 90, 100 66 Z" fill="url(#flamey-core)"/>
  <ellipse cx="78" cy="132" rx="11" ry="13" fill="{COCOA}"><animate attributeName="ry" values="13;13;1.5;13;13" keyTimes="0;0.9;0.93;0.96;1" dur="4s" repeatCount="indefinite"/></ellipse>
  <ellipse cx="122" cy="132" rx="11" ry="13" fill="{COCOA}"><animate attributeName="ry" values="13;13;1.5;13;13" keyTimes="0;0.9;0.93;0.96;1" dur="4s" repeatCount="indefinite"/></ellipse>
  <circle cx="74" cy="127" r="3.5" fill="#fff"><animate attributeName="opacity" values="1;1;0;1;1" keyTimes="0;0.9;0.93;0.96;1" dur="4s" repeatCount="indefinite"/></circle>
  <circle cx="118" cy="127" r="3.5" fill="#fff"><animate attributeName="opacity" values="1;1;0;1;1" keyTimes="0;0.9;0.93;0.96;1" dur="4s" repeatCount="indefinite"/></circle>
  <path d="M78 152 C 86 172, 114 172, 122 152 Z" fill="{COCOA}"/>
  <path d="M90 164 C 96 170, 104 170, 110 164 C 106 160, 94 160, 90 164 Z" fill="#ff6f7d"/>
</g>"""


def chip(x, y, text, accent):
    w = round(len(text) * 8.6 + 34)
    return (
        f'<g transform="translate({x} {y})">'
        f'<rect width="{w}" height="34" rx="17" fill="#ffffff" fill-opacity="0.06" stroke="#ffffff" stroke-opacity="0.12"/>'
        f'<circle cx="17" cy="17" r="4" fill="{accent}"/>'
        f'<text x="29" y="22.5" font-family="{FONT}" font-size="15" fill="#e7e1db">{escape(text)}</text></g>',
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


def fetch_live():
    """Live numbers for the header. Falls back to the last saved values if a source is down."""
    cache_path = ASSETS / "live.json"
    try:
        live = json.loads(cache_path.read_text())
    except Exception:
        live = {}
    try:
        with urllib.request.urlopen("https://mad.mindgoblin.tech/public/stats", timeout=15) as r:
            s = json.load(r)
        live["mad"] = {k: s[k] for k in ("total_users", "total_miles", "miles_today")}
    except Exception as e:
        print("Mile A Day stats unavailable, keeping last values:", e)
    try:
        url = "https://raw.githubusercontent.com/robwizzie/top-dogs-pool/main/data/apa.json"
        with urllib.request.urlopen(url, timeout=15) as r:
            team = json.load(r)["team"]
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
    omw_w = 40  # running Flamey width at 0.2 scale
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
  <g transform="translate(948 40) scale(0.72)">
    <g><animateTransform attributeName="transform" type="translate" values="0 0;0 -8;0 0" dur="2.4s" repeatCount="indefinite"/>
    {flamey("wave")}</g>
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
    <g transform="translate(0 {line_y - 46}) scale(0.2)">
      <g><animateTransform attributeName="transform" type="translate" values="0 0;0 -14;0 0" dur="0.225s" repeatCount="indefinite"/>
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

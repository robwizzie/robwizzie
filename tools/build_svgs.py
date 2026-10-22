"""Builds the animated SVGs used in the profile README.

Run from the repo root:  python3 tools/build_svgs.py
Flamey stickers come from the Mile A Day app (robwizzie/Mile-A-Day).
"""
import base64
import io
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
STICKERS = ROOT / "tools" / "stickers"
FONT = "'Segoe UI', -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def b64(name, height):
    im = Image.open(STICKERS / f"{name}.png").convert("RGBA")
    w = round(im.width * height * 2 / im.height)
    im = im.resize((w, height * 2), Image.LANCZOS)  # 2x for retina
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode(), w // 2


def typing_lines(lines, x, y, size, color, per=3.2):
    """Each line types out, holds, then erases; lines take turns forever."""
    total = per * len(lines)
    out = []
    for i, text in enumerate(lines):
        n = len(text)
        width = n * size * 0.6 + 4  # monospace advance ~0.6em
        start, end = i * per / total, (i + 1) * per / total
        type_end = start + (per * 0.45) / total
        erase_start = end - (per * 0.12) / total
        kt = f"0;{start:.4f};{type_end:.4f};{erase_start:.4f};{end:.4f};1"
        cid = f"tl{i}"
        out.append(
            f'<clipPath id="{cid}"><rect x="{x}" y="{y - size}" height="{size * 1.5}" width="0">'
            f'<animate attributeName="width" dur="{total}s" repeatCount="indefinite" calcMode="discrete" '
            f'keyTimes="0;{";".join(f"{start + (type_end - start) * k / n:.4f}" for k in range(n + 1))};1" '
            f'values="0;{";".join(f"{width * k / n:.1f}" for k in range(n + 1))};0"/>'
            f"</rect></clipPath>"
        )
        # keep the line hidden outside its slot (discrete timing above restarts at 0 width)
        out.append(
            f'<g clip-path="url(#{cid})" opacity="0">'
            f'<animate attributeName="opacity" dur="{total}s" repeatCount="indefinite" calcMode="discrete" '
            f'keyTimes="0;{start:.4f};{erase_start:.4f}" values="0;1;0"/>'
            f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" fill="{color}">{escape(text)}</text></g>'
        )
        # caret that follows the typed text
        cx = [x + 2 + width * k / n for k in range(n + 1)]
        out.append(
            f'<rect y="{y - size * 0.85}" width="{size * 0.55:.1f}" height="{size * 1.05:.1f}" fill="{color}" opacity="0">'
            f'<animate attributeName="x" dur="{total}s" repeatCount="indefinite" calcMode="discrete" '
            f'keyTimes="0;{";".join(f"{start + (type_end - start) * k / n:.4f}" for k in range(n + 1))}" '
            f'values="{cx[0]:.1f};{";".join(f"{c:.1f}" for c in cx)}"/>'
            f'<animate attributeName="opacity" dur="{total}s" repeatCount="indefinite" calcMode="discrete" '
            f'keyTimes="0;{start:.4f};{erase_start:.4f}" values="0;1;0"/></rect>'
        )
    return "\n".join(out)


def stars(n, w, h, seed=7):
    import random

    r = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = r.uniform(0, w), r.uniform(0, h)
        rad = r.choice([0.8, 1, 1.2, 1.6])
        d = r.uniform(2, 5)
        b = r.uniform(0, 4)
        out.append(
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rad}" fill="#fff">'
            f'<animate attributeName="opacity" values="0.15;0.9;0.15" dur="{d:.1f}s" begin="-{b:.1f}s" repeatCount="indefinite"/></circle>'
        )
    return "\n".join(out)


def header():
    W, H = 1200, 360
    hi, hi_w = b64("hiii", 190)
    omw, omw_w = b64("omw", 56)
    lines = [
        "co-founder of Mile A Day: one mile, every single day",
        "full-stack + iOS dev out of South Jersey",
        "i build apps for my friends, my pool team & LeBron fans",
        "currently: turning my TV into a custom home screen",
        "shipping side projects faster than i finish them",
    ]
    track_y = 306
    run = 9  # seconds per lap
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Hey, I'm Rob. Flamey runs a mile across the bottom.">
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0.35" y2="1">
    <stop offset="0" stop-color="#0d0b1e"/><stop offset="0.6" stop-color="#2a0c1d"/><stop offset="1" stop-color="#4a1018"/>
  </linearGradient>
  <linearGradient id="glow" x1="0" x2="1"><stop offset="0" stop-color="#ffb347"/><stop offset="1" stop-color="#ff4d4d"/></linearGradient>
  <radialGradient id="halo" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#ff7a2f" stop-opacity="0.45"/><stop offset="1" stop-color="#ff7a2f" stop-opacity="0"/></radialGradient>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath>
</defs>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="url(#sky)"/>
{stars(70, W, 250)}

<!-- name -->
<g font-family="{FONT}">
  <text x="64" y="118" font-size="64" font-weight="800" fill="#fff">Hey, I'm Rob
    <animate attributeName="opacity" values="0;1" dur="0.8s" fill="freeze"/></text>
  <g transform="translate(470 96)">
    <text font-size="54" x="0" y="0">👋
      <animateTransform attributeName="transform" type="rotate" values="0 20 -10;18 20 -10;-8 20 -10;18 20 -10;0 20 -10;0 20 -10" keyTimes="0;0.1;0.2;0.3;0.4;1" dur="2.6s" repeatCount="indefinite"/></text>
  </g>
  <text x="66" y="160" font-size="22" font-weight="600" fill="url(#glow)" letter-spacing="1.5">ROB WISCOUNT · @robwizzie</text>
</g>
<text x="66" y="202" font-family="{MONO}" font-size="20" fill="#ff8a5c">&gt;</text>
{typing_lines(lines, 88, 202, 20, '#f4ece6')}

<!-- waving flamey -->
<circle cx="1000" cy="140" r="150" fill="url(#halo)">
  <animate attributeName="r" values="140;158;140" dur="2.4s" repeatCount="indefinite"/></circle>
<image href="{hi}" x="{1000 - hi_w / 2:.0f}" y="40" width="{hi_w}" height="190">
  <animateTransform attributeName="transform" type="translate" values="0 0;0 -8;0 0" dur="1.8s" repeatCount="indefinite"/>
</image>

<!-- running track -->
<rect x="0" y="{track_y - 14}" width="{W}" height="56" fill="#9b2a1f"/>
<rect x="0" y="{track_y - 14}" width="{W}" height="56" fill="#000" opacity="0.18"/>
<line x1="0" y1="{track_y - 14}" x2="{W}" y2="{track_y - 14}" stroke="#f4ece6" stroke-width="3" opacity="0.85"/>
<line x1="0" y1="{track_y + 14}" x2="{W}" y2="{track_y + 14}" stroke="#f4ece6" stroke-width="2" stroke-dasharray="26 18" opacity="0.5">
  <animate attributeName="stroke-dashoffset" values="0;-44" dur="0.5s" repeatCount="indefinite"/></line>
<line x1="0" y1="{track_y + 41}" x2="{W}" y2="{track_y + 41}" stroke="#f4ece6" stroke-width="3" opacity="0.85"/>
<g font-family="{MONO}" font-size="13" fill="#f4ece6" opacity="0.75">
  <text x="{W - 128}" y="{track_y - 22}">FINISH · 1.00 mi</text>
</g>
<rect x="{W - 30}" y="{track_y - 14}" width="10" height="56" fill="#f4ece6" opacity="0.9"/>

<!-- flamey runs the mile, trail behind -->
<g>
  <animateTransform attributeName="transform" type="translate" values="-120 0;{W - 60} 0;{W - 60} 0" keyTimes="0;0.86;1" dur="{run}s" repeatCount="indefinite"/>
  <rect x="-60" y="{track_y - 6}" width="80" height="6" rx="3" fill="url(#glow)" opacity="0.55"/>
  <rect x="-110" y="{track_y + 6}" width="120" height="4" rx="2" fill="url(#glow)" opacity="0.35"/>
  <image href="{omw}" x="0" y="{track_y - 50}" width="{omw_w}" height="56">
    <animateTransform attributeName="transform" type="translate" values="0 0;0 -6;0 0" dur="0.32s" repeatCount="indefinite"/>
  </image>
</g>
<!-- mile counter -->
<g font-family="{MONO}" font-weight="700">
  <rect x="64" y="222" width="232" height="34" rx="10" fill="#000" opacity="0.35"/>
  <text x="80" y="245" font-size="16" fill="#ffb347">MILE</text>
  {mile_counter(132, 245, run)}
  <text x="212" y="245" font-size="16" fill="#ff8a5c">🔥 still lit</text>
</g>
</g>
</svg>"""


def mile_counter(x, y, run):
    vals = [f"{k / 20:.2f}" for k in range(21)]
    n = len(vals)
    out = []
    lap = 0.86
    for i, v in enumerate(vals):
        a, b = lap * i / (n - 1), lap * (i + 1) / (n - 1) if i < n - 1 else 1
        out.append(
            f'<text x="{x}" y="{y}" font-size="16" fill="#fff" opacity="0">{v}'
            f'<animate attributeName="opacity" dur="{run}s" repeatCount="indefinite" calcMode="discrete" '
            f'keyTimes="0;{a:.4f};{min(b, 1):.4f}" values="0;1;0"/></text>'
        )
    return "\n".join(out)


def footer():
    W, H = 1200, 120
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#4a1018"/><stop offset="1" stop-color="#0d0b1e"/></linearGradient></defs>
<path fill="url(#g)" opacity="0.55">
  <animate attributeName="d" dur="7s" repeatCount="indefinite" values="
  M0 60 C 200 20, 400 100, 600 60 S 1000 20, 1200 60 V120 H0Z;
  M0 60 C 200 100, 400 20, 600 60 S 1000 100, 1200 60 V120 H0Z;
  M0 60 C 200 20, 400 100, 600 60 S 1000 20, 1200 60 V120 H0Z"/></path>
<path fill="url(#g)">
  <animate attributeName="d" dur="5s" repeatCount="indefinite" values="
  M0 80 C 250 50, 450 110, 650 80 S 1000 50, 1200 80 V120 H0Z;
  M0 80 C 250 110, 450 50, 650 80 S 1000 110, 1200 80 V120 H0Z;
  M0 80 C 250 50, 450 110, 650 80 S 1000 50, 1200 80 V120 H0Z"/></path>
</svg>"""


def pool_divider():
    """Cue ball rolls in, kisses the 8, the 8 drops in the corner pocket. Loops."""
    W, H, y = 1200, 90, 45
    d = 6  # seconds
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Cue ball sinks the 8-ball">
<defs>
  <linearGradient id="felt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0f5132"/><stop offset="1" stop-color="#0a3a24"/></linearGradient>
  <radialGradient id="cue" cx="0.35" cy="0.3" r="0.7"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#cfcfcf"/></radialGradient>
  <radialGradient id="eight" cx="0.35" cy="0.3" r="0.7"><stop offset="0" stop-color="#555"/><stop offset="1" stop-color="#050505"/></radialGradient>
  <clipPath id="c"><rect x="0" y="0" width="{W}" height="{H}" rx="18"/></clipPath>
</defs>
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="#5a3a22"/>
  <rect x="10" y="10" width="{W - 20}" height="{H - 20}" rx="12" fill="url(#felt)"/>
  <g fill="#e9d8a6" opacity="0.8">{"".join(f'<circle cx="{x}" cy="5" r="2"/><circle cx="{x}" cy="{H - 5}" r="2"/>' for x in range(150, W - 100, 150))}</g>
  <circle cx="{W - 30}" cy="{y}" r="17" fill="#050505"/>
  <!-- cue stick strike -->
  <g>
    <animateTransform attributeName="transform" type="translate" values="80 0;40 0;122 0;-400 0;-400 0" keyTimes="0;0.12;0.16;0.3;1" dur="{d}s" repeatCount="indefinite"/>
    <rect x="-260" y="{y - 4}" width="250" height="8" rx="4" fill="#c8915a"/>
    <rect x="-22" y="{y - 4}" width="12" height="8" rx="3" fill="#e6f0ff"/>
  </g>
  <!-- cue ball -->
  <circle cx="0" cy="{y}" r="14" fill="url(#cue)">
    <animate attributeName="cx" values="130;130;780;790;790;130" keyTimes="0;0.16;0.5;0.56;0.94;1" dur="{d}s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;0.9;0.94;0.99;1" dur="{d}s" repeatCount="indefinite"/>
  </circle>
  <!-- 8 ball -->
  <g>
    <animateTransform attributeName="transform" type="translate" values="0 0;0 0;{W - 30 - 812} 0;{W - 30 - 812} 0;0 0" keyTimes="0;0.5;0.78;0.97;1" dur="{d}s" repeatCount="indefinite"/>
    <circle cx="812" cy="{y}" r="14" fill="url(#eight)">
      <animate attributeName="r" values="14;14;0;0;14" keyTimes="0;0.76;0.82;0.97;1" dur="{d}s" repeatCount="indefinite"/></circle>
    <circle cx="812" cy="{y}" r="6" fill="#fff">
      <animate attributeName="r" values="6;6;0;0;6" keyTimes="0;0.76;0.82;0.97;1" dur="{d}s" repeatCount="indefinite"/></circle>
    <text x="812" y="{y + 3.5}" text-anchor="middle" font-family="{FONT}" font-size="9" font-weight="800" fill="#000">8
      <animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;0.76;0.78;0.97;1" dur="{d}s" repeatCount="indefinite"/></text>
  </g>
  <text x="{W / 2}" y="{y + 6}" text-anchor="middle" font-family="{MONO}" font-size="15" fill="#e9d8a6" opacity="0">
    8-ball, corner pocket · Top Dawgs 🎱
    <animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.8;0.84;0.95;1" dur="{d}s" repeatCount="indefinite"/></text>
</g>
</svg>"""


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "header.svg").write_text(header())
    (ASSETS / "footer.svg").write_text(footer())
    (ASSETS / "pool.svg").write_text(pool_divider())
    for f in ("header.svg", "footer.svg", "pool.svg"):
        print(f, (ASSETS / f).stat().st_size // 1024, "KB")

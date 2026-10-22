"""Builds the animated header used in the profile README.

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


def header_clean():
    """Quiet banner: name, role, and Flamey jogging along a thin line."""
    W, H = 1200, 240
    omw, omw_w = b64("omw", 44)
    line_y = 206
    run = 14
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Rob Wiscount, full-stack and iOS developer">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#14141a"/><stop offset="1" stop-color="#2a1216"/>
  </linearGradient>
  <linearGradient id="fade" x1="0" x2="1">
    <stop offset="0" stop-color="#e2554a" stop-opacity="0"/><stop offset="0.5" stop-color="#e2554a" stop-opacity="0.6"/><stop offset="1" stop-color="#e2554a" stop-opacity="0"/>
  </linearGradient>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="16"/></clipPath>
</defs>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <g font-family="{FONT}">
    <text x="64" y="104" font-size="52" font-weight="700" fill="#f5f2ee" letter-spacing="-0.5">Rob Wiscount</text>
    <text x="66" y="146" font-size="22" fill="#b9b2ab">Full-stack and iOS developer · Co-founder of Mile A Day</text>
  </g>
  <rect x="0" y="{line_y}" width="{W}" height="1.5" fill="url(#fade)"/>
  <g>
    <animateTransform attributeName="transform" type="translate" values="-80 0;{W + 20} 0" dur="{run}s" repeatCount="indefinite"/>
    <image href="{omw}" x="0" y="{line_y - 44}" width="{omw_w}" height="44">
      <animateTransform attributeName="transform" type="translate" values="0 0;0 -3;0 0" dur="0.4s" repeatCount="indefinite"/>
    </image>
  </g>
</g>
</svg>"""


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "header.svg").write_text(header_clean())
    print("header.svg", (ASSETS / "header.svg").stat().st_size // 1024, "KB")

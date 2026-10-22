"""Build the 1200x675 project preview cards used in the profile README.

usage: python3 tools/cards.py <name> <style> <bg_top> <bg_bottom> <img> [<img> ...]
  style "phones":  1-4 phone screenshots side by side
  style "desktop": one desktop screenshot in a browser frame (+ optional phone overlay)
  style "fill":    one image cropped to fill the card
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

W, H = 1200, 675
OUT = Path(__file__).resolve().parent.parent / "assets" / "projects"


def hexc(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def gradient(top, bot):
    t, b = hexc(top), hexc(bot)
    g = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(g)
    for y in range(H):
        k = y / (H - 1)
        d.line([(0, y), (W, y)], fill=tuple(int(t[i] + (b[i] - t[i]) * k) for i in range(3)) + (255,))
    return g


def rounded(im, r):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, im.size[0] - 1, im.size[1] - 1], r, fill=255)
    im = im.convert("RGBA")
    a = im.getchannel("A")
    from PIL import ImageChops
    im.putalpha(ImageChops.multiply(a, m))
    return im


def drop(canvas, im, xy, blur=18, off=(0, 16), alpha=0.5):
    s = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 255))
    sh.putalpha(im.getchannel("A").point(lambda a: int(a * alpha)))
    s.alpha_composite(sh, (xy[0] + off[0], xy[1] + off[1]))
    canvas.alpha_composite(s.filter(ImageFilter.GaussianBlur(blur)))
    canvas.alpha_composite(im, xy)


def phones(bg, files):
    ph = 560 if len(files) >= 3 else 590
    ims = []
    for f in files:
        im = Image.open(f).convert("RGB")
        w = round(im.width * ph / im.height)
        ims.append(rounded(im.resize((w, ph), Image.LANCZOS), int(w * 0.12)))
    gap = 34
    total = sum(i.width for i in ims) + gap * (len(ims) - 1)
    if total > W - 60:  # shrink to fit
        k = (W - 60) / total
        ims = [i.resize((int(i.width * k), int(i.height * k)), Image.LANCZOS) for i in ims]
        total = sum(i.width for i in ims) + gap * (len(ims) - 1)
    x = (W - total) // 2
    for i in ims:
        drop(bg, i, (x, (H - i.height) // 2))
        x += i.width + gap


def desktop(bg, files):
    shot = Image.open(files[0]).convert("RGB")
    bw = 1040 if len(files) == 1 else 900
    bh = round(shot.height * bw / shot.width)
    bh = min(bh, 560)
    shot = shot.resize((bw, round(shot.height * bw / shot.width)), Image.LANCZOS).crop((0, 0, bw, bh))
    bar = 34
    frame = Image.new("RGBA", (bw, bh + bar), (30, 30, 34, 255))
    d = ImageDraw.Draw(frame)
    for k, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        d.ellipse([16 + k * 22, 11, 28 + k * 22, 23], fill=c)
    frame.paste(shot, (0, bar))
    frame = rounded(frame, 14)
    x = (W - bw) // 2 if len(files) == 1 else 50
    y = (H - frame.height) // 2
    drop(bg, frame, (x, y))
    if len(files) > 1:
        p = Image.open(files[1]).convert("RGB")
        ph = 520
        pw = round(p.width * ph / p.height)
        p = rounded(p.resize((pw, ph), Image.LANCZOS), int(pw * 0.12))
        drop(bg, p, (W - pw - 60, H - ph - 40), blur=22, alpha=0.6)


def fit(bg, files):
    im = Image.open(files[0]).convert("RGBA")
    k = min((W - 40) / im.width, (H - 40) / im.height)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    bg.alpha_composite(im, ((W - im.width) // 2, (H - im.height) // 2))


def fill(bg, files):
    im = Image.open(files[0]).convert("RGB")
    k = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    l, t = (im.width - W) // 2, (im.height - H) // 2
    bg.alpha_composite(im.crop((l, t, l + W, t + H)).convert("RGBA"))


if __name__ == "__main__":
    name, style, top, bot, *files = sys.argv[1:]
    bg = gradient(top, bot)
    {"phones": phones, "desktop": desktop, "fill": fill, "fit": fit}[style](bg, files)
    bg = rounded(bg, 28)
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / f"{name}.png"
    bg.save(out, optimize=True)
    print(out.name, out.stat().st_size // 1024, "KB")

"""Generate the icon / social-card assets the <head> references.

Everything is drawn from code (a parametric heart), so the repo carries no
third-party artwork and nothing is licensed in from anywhere.
"""
import math, pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs"
SS = 4                                   # supersample factor for smooth edges

PINK_BG_TOP = (255, 233, 242)
PINK_BG_BOT = (253, 238, 230)
HEART = (242, 109, 141)
HEART_DARK = (214, 78, 110)
INK = (61, 107, 158)
GREY = (122, 106, 130)


def heart_points(cx, cy, size, steps=240):
    """Classic parametric heart curve, scaled so `size` is roughly its width."""
    pts = []
    for i in range(steps):
        t = 2 * math.pi * i / steps
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * size / 32.0, cy - y * size / 32.0))
    return pts


def bg(w, h):
    img = Image.new("RGB", (w, h), PINK_BG_TOP)
    d = ImageDraw.Draw(img)
    for y in range(h):
        f = y / max(1, h - 1)
        d.line([(0, y), (w, y)], fill=tuple(
            round(PINK_BG_TOP[i] + (PINK_BG_BOT[i] - PINK_BG_TOP[i]) * f) for i in range(3)))
    return img


def icon(size, heart_frac, bg_alpha=True, rounded=True):
    s = size * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if bg_alpha:
        d.rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * 0.22), fill=(255, 240, 246, 255))
        d.ellipse([-s * 0.25, -s * 0.35, s * 0.95, s * 0.75], fill=(255, 226, 238, 255))
    d.polygon(heart_points(s / 2, s * 0.55, s * heart_frac), fill=HEART)
    d.polygon(heart_points(s / 2 - s * 0.012, s * 0.535, s * heart_frac * 0.9), fill=HEART)
    # a soft highlight so the mark is not a flat blob
    d.ellipse([s * 0.30, s * 0.28, s * 0.42, s * 0.40], fill=(255, 190, 210, 235))
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    if rounded:
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], radius=int(size * 0.22), fill=255)
        img.putalpha(mask)
    return img


def font(px, bold=True):
    for name in (("segoeuib.ttf", "arialbd.ttf") if bold else ("segoeui.ttf", "arial.ttf")):
        p = pathlib.Path(r"C:\Windows\Fonts") / name
        if p.exists():
            return ImageFont.truetype(str(p), px)
    return ImageFont.load_default()


def fit_font(draw, text, px, max_w, bold=True):
    """Shrink until the string actually fits — the first draft clipped off-canvas."""
    while px > 8:
        f = font(px, bold)
        if draw.textlength(text, font=f) <= max_w:
            return f
        px -= 2
    return font(8, bold)


def cover(w=1200, h=630):
    s = SS
    img = bg(w * s, h * s)
    d = ImageDraw.Draw(img, "RGBA")
    # warm corner glow + soft hills so the card is not a flat wash
    d.ellipse([w * s * 0.62, -h * s * 0.55, w * s * 1.35, h * s * 0.75], fill=(255, 236, 214, 190))
    d.ellipse([-w * s * 0.15, h * s * 0.80, w * s * 0.55, h * s * 1.35], fill=(255, 214, 230, 150))
    # heart mark
    hx, hy, hs = int(w * s * 0.19), int(h * s * 0.44), int(w * s * 0.17)
    d.polygon(heart_points(hx, hy, hs), fill=HEART)
    d.polygon(heart_points(hx - hs * 0.03, hy - hs * 0.03, hs * 0.88), fill=HEART)
    d.ellipse([hx - hs * 0.22, hy - hs * 0.34, hx - hs * 0.08, hy - hs * 0.20], fill=(255, 196, 214, 240))
    # headline block, every line auto-fitted to the remaining width
    tx = int(w * s * 0.36)
    maxw = w * s - tx - int(56 * s)
    lines = [
        ("Iman Donation Trust",                    58, INK,       True,  0.20),
        ("Donate your things, anywhere in Pakistan", 34, GREY,     False, 0.42),
        ("34 partner sites  ·  17 cities  ·  7 regions", 30, HEART_DARK, False, 0.56),
        ("Ticket in seconds  ·  no account  ·  nothing uploaded", 26, GREY, False, 0.69),
    ]
    for text, px, colour, bold, yfrac in lines:
        d.text((tx, int(h * s * yfrac)), text, font=fit_font(d, text, int(px * s), maxw, bold), fill=colour)
    bar_y = int(h * s * 0.83)
    d.rounded_rectangle([tx, bar_y, tx + int(300 * s), bar_y + int(9 * s)],
                        radius=int(5 * s), fill=(242, 109, 141, 190))
    img = img.resize((w, h), Image.Resampling.LANCZOS)
    img.save(OUT / "og-cover.png", "PNG", optimize=True)
    print("og-cover.png", img.size)


def main():
    icon(180, 0.62).save(OUT / "apple-touch-icon.png", "PNG")
    print("apple-touch-icon.png 180x180")
    for n in (192, 512):
        icon(n, 0.60).save(OUT / f"icon-{n}.png", "PNG")
        print(f"icon-{n}.png {n}x{n}")
    cover()


if __name__ == "__main__":
    main()

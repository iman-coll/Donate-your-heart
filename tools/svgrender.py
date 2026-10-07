"""Minimal SVG -> Pillow rasteriser for the art this app generates.

Supports exactly the subset the app emits: svg(viewBox), g(transform), rect (with rx),
circle, ellipse, path (M/L/H/V/Z/a/q/c), fill, stroke, stroke-width, opacity and the
hex/rgba colours used. Flattened to polygons, so it approximates curves — good enough
to answer "does this look like the character I meant".

(preview_companion.py keeps its own copy of the child-scene renderer; it is bespoke
about the scene's depth layers and was verified separately.)
"""
import math, re
from PIL import Image, ImageDraw

TAU = math.pi * 2


def colour(c):
    if c is None:
        return None
    c = c.strip()
    if c in ("none", "transparent", ""):
        return None
    m = re.match(r"rgba?\(([^)]+)\)", c)
    if m:
        p = [x.strip() for x in m.group(1).split(",")]
        r, g, b = (int(float(p[i])) for i in range(3))
        a = int(float(p[3]) * 255) if len(p) > 3 else 255
        return (r, g, b, a)
    if c.startswith("#"):
        h = c[1:]
        if len(h) == 3:
            h = "".join(ch * 2 for ch in h)
        if len(h) >= 6:
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)
    return (128, 128, 128, 255)


def _mul(m, n):
    return [m[0] * n[0] + m[2] * n[1], m[1] * n[0] + m[3] * n[1],
            m[0] * n[2] + m[2] * n[3], m[1] * n[2] + m[3] * n[3],
            m[0] * n[4] + m[2] * n[5] + m[4], m[1] * n[4] + m[3] * n[5] + m[5]]


def matrix(txt):
    m = [1, 0, 0, 1, 0, 0]
    if not txt:
        return m
    for fn, args in re.findall(r"(\w+)\(([^)]*)\)", txt):
        v = [float(x) for x in re.split(r"[\s,]+", args.strip()) if x]
        if not v:
            continue
        if fn == "translate":
            n = [1, 0, 0, 1, v[0], v[1] if len(v) > 1 else 0]
        elif fn == "scale":
            n = [v[0], 0, 0, v[1] if len(v) > 1 else v[0], 0, 0]
        elif fn == "rotate":
            a = math.radians(v[0]); c, s = math.cos(a), math.sin(a)
            n = [c, s, -s, c, 0, 0]
            if len(v) > 2:
                n = [c, s, -s, c, v[1] - c * v[1] + s * v[2], v[2] - s * v[1] - c * v[2]]
        elif fn == "matrix":
            n = v[:6]
        else:
            continue
        m = _mul(m, n)
    return m


def ap(m, x, y):
    return (m[0] * x + m[2] * y + m[4], m[1] * x + m[3] * y + m[5])


def path_points(d):
    """Flatten an SVG path into polylines. Supports M L H V Z a q c."""
    toks = re.findall(r"[MmLlHhVvZzAaQqCcSs]|-?\d*\.?\d+(?:e-?\d+)?", d)
    out, cur, start = [], (0.0, 0.0), (0.0, 0.0)
    NEED = {"M": 2, "m": 2, "L": 2, "l": 2, "H": 1, "h": 1, "V": 1, "v": 1,
            "Q": 4, "q": 4, "C": 6, "c": 6, "A": 7, "a": 7}

    def seg():
        if not out:
            out.append([cur])
        return out[-1]

    def run(cmd, nums):
        nonlocal cur, start
        k = 0
        while True:
            if cmd in ("Z", "z"):
                if out:
                    out[-1].append(start)
                cur = start
                return
            need = NEED.get(cmd)
            if need is None or k + need > len(nums):
                return
            if cmd in ("M", "m"):
                x, y = (nums[k], nums[k + 1]) if cmd == "M" else (cur[0] + nums[k], cur[1] + nums[k + 1])
                cur = (x, y); start = cur; out.append([cur]); k += 2
                cmd = "L" if cmd == "M" else "l"
                continue
            s = seg()
            if cmd in ("L", "l"):
                cur = ((nums[k], nums[k + 1]) if cmd == "L"
                       else (cur[0] + nums[k], cur[1] + nums[k + 1]))
                s.append(cur); k += 2
            elif cmd in ("H", "h"):
                cur = (nums[k] if cmd == "H" else cur[0] + nums[k], cur[1]); s.append(cur); k += 1
            elif cmd in ("V", "v"):
                cur = (cur[0], nums[k] if cmd == "V" else cur[1] + nums[k]); s.append(cur); k += 1
            elif cmd in ("Q", "q"):
                cx, cy, x, y = nums[k:k + 4]
                if cmd == "q":
                    cx, cy, x, y = cur[0] + cx, cur[1] + cy, cur[0] + x, cur[1] + y
                for i in range(1, 13):
                    t = i / 12
                    s.append(((1 - t) ** 2 * cur[0] + 2 * (1 - t) * t * cx + t * t * x,
                              (1 - t) ** 2 * cur[1] + 2 * (1 - t) * t * cy + t * t * y))
                cur = (x, y); k += 4
            elif cmd in ("C", "c"):
                x1, y1, x2, y2, x, y = nums[k:k + 6]
                if cmd == "c":
                    x1, y1 = cur[0] + x1, cur[1] + y1
                    x2, y2 = cur[0] + x2, cur[1] + y2
                    x, y = cur[0] + x, cur[1] + y
                for i in range(1, 13):
                    t = i / 12; u = 1 - t
                    s.append((u ** 3 * cur[0] + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t ** 3 * x,
                              u ** 3 * cur[1] + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t ** 3 * y))
                cur = (x, y); k += 6
            elif cmd in ("A", "a"):
                rx, ry, rot, laf, sf, x, y = nums[k:k + 7]
                if cmd == "a":
                    x, y = cur[0] + x, cur[1] + y
                if rx == 0 or ry == 0:
                    s.append((x, y))
                else:
                    phi = math.radians(rot)
                    dx2, dy2 = (cur[0] - x) / 2, (cur[1] - y) / 2
                    x1p = math.cos(phi) * dx2 + math.sin(phi) * dy2
                    y1p = -math.sin(phi) * dx2 + math.cos(phi) * dy2
                    lam = x1p ** 2 / rx ** 2 + y1p ** 2 / ry ** 2
                    if lam > 1:
                        sc = math.sqrt(lam); rx *= sc; ry *= sc
                    num = rx ** 2 * ry ** 2 - rx ** 2 * y1p ** 2 - ry ** 2 * x1p ** 2
                    den = rx ** 2 * y1p ** 2 + ry ** 2 * x1p ** 2
                    co = math.sqrt(max(0.0, num / den)) * (-1 if laf == sf else 1)
                    cxp, cyp = co * rx * y1p / ry, -co * ry * x1p / rx
                    ccx = math.cos(phi) * cxp - math.sin(phi) * cyp + (cur[0] + x) / 2
                    ccy = math.sin(phi) * cxp + math.cos(phi) * cyp + (cur[1] + y) / 2
                    a1 = math.atan2((y1p - cyp) / ry, (x1p - cxp) / rx)
                    a2 = math.atan2((-y1p - cyp) / ry, (-x1p - cxp) / rx)
                    da = a2 - a1
                    if sf == 0 and da > 0:
                        da -= TAU
                    elif sf == 1 and da < 0:
                        da += TAU
                    for i in range(1, 25):
                        a = a1 + da * i / 24
                        s.append((ccx + rx * math.cos(a) * math.cos(phi) - ry * math.sin(a) * math.sin(phi),
                                  ccy + rx * math.cos(a) * math.sin(phi) + ry * math.sin(a) * math.cos(phi)))
                cur = (x, y); k += 7

    cmd, nums, i = None, [], 0
    while i < len(toks):
        t = toks[i]
        if re.match(r"[A-Za-z]", t):
            if cmd is not None and (nums or cmd in ("Z", "z")):
                run(cmd, nums)
            nums = []; cmd = t; i += 1
            if cmd in ("Z", "z"):
                run(cmd, []); cmd = None
        else:
            nums.append(float(t)); i += 1
    if cmd is not None and nums:
        run(cmd, nums)
    return out


def _round_rect(x, y, w, h, r):
    if isinstance(r, (int, float)):
        r = [r] * 4
    tl, tr, br, bl = r
    pts = []

    def P(px, py):
        pts.append((px, py))

    def Q(px, py, rad, a0):
        for i in range(1, 9):
            a = a0 + (math.pi / 2) * i / 8
            P(px + math.cos(a) * rad, py + math.sin(a) * rad)

    P(x + tl, y); P(x + w - tr, y); Q(x + w - tr, y + tr, tr, -math.pi / 2)
    P(x + w, y + h - br); Q(x + w - br, y + h - br, br, 0)
    P(x + bl, y + h); Q(x + bl, y + h - bl, bl, math.pi / 2)
    P(x, y + tl); Q(x + tl, y + tl, tl, math.pi)
    return [pts]


def _shapes(el, m, scale):
    """Return (fills, strokes) as lists of (points, colour, width)."""
    tag = el.tag.split("}")[-1].lower()
    fill = colour(el.get("fill"))
    stroke = colour(el.get("stroke"))
    sw = float(el.get("stroke-width") or 0) * scale
    op = el.get("opacity")
    if op:
        o = float(op)
        fill = tuple(list(fill[:3]) + [int(fill[3] * o)]) if fill else None
        stroke = tuple(list(stroke[:3]) + [int(stroke[3] * o)]) if stroke else None
    polys = []
    if tag == "rect":
        x, y = float(el.get("x") or 0), float(el.get("y") or 0)
        w, h = float(el.get("width") or 0), float(el.get("height") or 0)
        rx = el.get("rx")
        if w <= 0 or h <= 0:
            return [], [], 0
        polys = _round_rect(x, y, w, h, float(rx) if rx else 0)
    elif tag == "circle":
        cx, cy = float(el.get("cx") or 0), float(el.get("cy") or 0)
        r = float(el.get("r") or 0)
        polys = [[(cx + math.cos(TAU * i / 40) * r, cy + math.sin(TAU * i / 40) * r) for i in range(41)]]
    elif tag == "ellipse":
        cx, cy = float(el.get("cx") or 0), float(el.get("cy") or 0)
        rx, ry = float(el.get("rx") or 0), float(el.get("ry") or 0)
        polys = [[(cx + math.cos(TAU * i / 40) * rx, cy + math.sin(TAU * i / 40) * ry) for i in range(41)]]
    elif tag == "path":
        d = el.get("d")
        if d:
            polys = path_points(d)
    else:
        return [], [], 0
    polys = [[ap(m, px, py) for px, py in poly] for poly in polys]
    fills = [(p, fill) for p in polys if fill and len(p) > 2]
    strokes = [(p, stroke) for p in polys if stroke and len(p) > 1]
    return fills, strokes, sw


def render(svg_el, scale=4, bg=(255, 255, 255, 255)):
    vb = [float(x) for x in re.split(r"[\s,]+", svg_el.get("viewBox").strip()) if x]
    vw, vh = vb[2], vb[3]
    W, H = int(round(vw * scale)), int(round(vh * scale))
    img = Image.new("RGBA", (W, H), bg)

    def walk(el, m):
        nonlocal img
        m = _mul(m, matrix(el.get("transform")))
        tag = el.tag.split("}")[-1].lower()
        if tag != "svg":
            res = _shapes(el, m, scale)
            if res:
                fills, strokes, sw = res
                for pts, col in fills:
                    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                    ImageDraw.Draw(layer).polygon([tuple(p) for p in pts], fill=col)
                    img = Image.alpha_composite(img, layer)
                for pts, col in strokes:
                    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                    d = ImageDraw.Draw(layer)
                    xy = [tuple(p) for p in pts]
                    lw = max(1, int(round(sw)))
                    d.line(xy, fill=col, width=lw, joint="curve")
                    for p in (xy[0], xy[-1]):
                        d.ellipse([p[0] - lw / 2, p[1] - lw / 2, p[0] + lw / 2, p[1] + lw / 2], fill=col)
                    img = Image.alpha_composite(img, layer)
        for kid in el:
            walk(kid, m)

    walk(svg_el, [scale, 0, 0, scale, 0, 0])
    return img

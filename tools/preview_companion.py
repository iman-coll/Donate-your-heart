"""Composition preview for the inline companion SVG.

No SVG rasteriser is available in this environment (and the browser cannot run under
the sandbox), so this reads the REAL coordinates out of index.html and redraws them
with Pillow: rects, circles, ellipses and the M/L/H/V/Z/a/q path commands the scene
actually uses. It is an approximation of the rendering, not a reference renderer — its
job is to let a human confirm the composition (is that a child's face, are the eyes
level, is anything overlapping wrongly), not to validate the SVG grammar.
"""
import math, pathlib, re, sys
from PIL import Image, ImageDraw
from lxml import html as LH

ROOT = pathlib.Path(__file__).resolve().parent.parent
src = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
doc = LH.fromstring(src)
SS = 4
W, H = 320, 190
CANVAS = (W * SS, H * SS)

# first stop colour of each gradient, for a flat approximation
grads = {}
for g in doc.xpath("//*[translate(local-name(),'LG','lg')='lineargradient' or "
                   "translate(local-name(),'RG','rg')='radialgradient']"):
    stops = g.xpath(".//*[translate(local-name(),'S','s')='stop']")
    if stops:
        grads[g.get("id")] = stops[0].get("stop-color") or "#ffffff"


def colour(v, fallback="#ffffff"):
    if not v or v == "none":
        return None
    m = re.match(r"url\(#(.+?)\)", v)
    if m:
        return grads.get(m.group(1), fallback)
    return v


def pts(d):
    """Flatten an SVG path `d` into polylines. Supports M L H V Z a q c.

    `out` is shared across commands on purpose: a shape like `M.. V.. a.. V.. Z` is
    ONE polygon, and starting a fresh segment per command silently breaks the fill.
    """
    toks = re.findall(r"[MmLlHhVvZzAaQqCc]|-?\d*\.?\d+(?:e-?\d+)?", d)
    out = []
    cur, start = (0.0, 0.0), (0.0, 0.0)
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
                x, y = (nums[k], nums[k + 1]) if cmd == "L" else (cur[0] + nums[k], cur[1] + nums[k + 1])
                cur = (x, y); s.append(cur); k += 2
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
                    # endpoint -> centre parameterisation (SVG spec F.6.5)
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
                        da -= 2 * math.pi
                    elif sf == 1 and da < 0:
                        da += 2 * math.pi
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
            nums = []
            cmd = t
            i += 1
            if cmd in ("Z", "z"):
                run(cmd, [])
                cmd = None
        else:
            nums.append(float(t)); i += 1
    if cmd is not None and nums:
        run(cmd, nums)
    return out


def rgb(c):
    c = c.lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    return tuple(int(c[k:k + 2], 16) for k in (0, 2, 4))


def render():
    img = Image.new("RGB", CANVAS, "#ffe4ef")
    d = ImageDraw.Draw(img, "RGBA")
    # paint the far layer first, then mid, then the child, matching document order
    for g in doc.xpath("//*[local-name()='g'][contains(@class,'sc-far') or "
                       "contains(@class,'sc-mid') or contains(@class,'sc-child')]"):
        for el in g.iter():
            tag = el.tag if isinstance(el.tag, str) else ""
            tag = tag.split("}")[-1].lower()
            fill = colour(el.get("fill"))
            stroke = colour(el.get("stroke"))
            sw = float(el.get("stroke-width") or 0) * SS
            opa = float(el.get("opacity") or 1)
            if opa <= 0:
                continue
            if fill:
                fill = rgb(fill) + (int(255 * opa),)
            if stroke:
                stroke = rgb(stroke) + (int(255 * opa),)
            if tag == "rect":
                x, y = float(el.get("x") or 0) * SS, float(el.get("y") or 0) * SS
                w, h = float(el.get("width")) * SS, float(el.get("height")) * SS
                if h > 0 and w > 0:
                    d.rectangle([x, y, x + w, y + h], fill=fill, outline=stroke, width=max(1, int(sw)))
            elif tag == "circle":
                cx, cy, r = (float(el.get(k)) * SS for k in ("cx", "cy", "r"))
                d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=stroke, width=max(1, int(sw)))
            elif tag == "ellipse":
                cx, cy = float(el.get("cx")) * SS, float(el.get("cy")) * SS
                rx, ry = float(el.get("rx")) * SS, float(el.get("ry")) * SS
                d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=fill, outline=stroke, width=max(1, int(sw)))
            elif tag == "path":
                for seg in pts(el.get("d")):
                    xy = [(p[0] * SS, p[1] * SS) for p in seg]
                    if len(xy) > 2 and fill:
                        d.polygon(xy, fill=fill)
                    if stroke:
                        d.line(xy, fill=stroke, width=max(1, int(sw)), joint="curve")
    return img


img = render()
img = img.resize((W * 2, H * 2), Image.Resampling.LANCZOS)
out = ROOT / "tools" / "companion-preview.png"
img.save(out)
print("wrote", out, img.size)

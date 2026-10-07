"""Render the 16 cursor friends so a human can look at them.

Runs the REAL butterflySVG()/figureSVG() from index.html in Node, then rasterises the
strings with tools/svgrender.py. Also parses every one with lxml, which is a genuine
well-formedness test of the generated markup rather than a spot check.
"""
import json, pathlib, re, subprocess, sys, importlib.util
from PIL import Image, ImageDraw, ImageFont
from lxml import etree

ROOT = pathlib.Path(__file__).resolve().parent.parent
NODE = pathlib.Path(r"C:\Users\Dell\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe")
sys.path.insert(0, str(ROOT / "tools"))
import svgrender  # noqa: E402

body = re.search(r"<script[^>]*>(.*?)</script>",
                 (ROOT / "docs" / "index.html").read_text(encoding="utf-8"),
                 re.S).group(1)


def const_by_name(name):
    i = body.index(f"const {name}=")
    k = body.index("=", i) + 1
    depth = 0
    while True:
        ch = body[k]
        if ch in "{[(":
            depth += 1
        elif ch in "}])":
            depth -= 1
        elif ch == ";" and depth == 0:
            return body[i:k + 1]
        k += 1


def function_by_name(name):
    i = body.index(f"function {name}(")
    j = body.index("{", i)
    depth, k = 0, j
    while True:
        if body[k] == "{":
            depth += 1
        elif body[k] == "}":
            depth -= 1
            if depth == 0:
                return body[i:k + 1]
        k += 1


DRIVER = "\n".join(const_by_name(n) for n in
                   ("BFLY_WINGS", "BUTTERFLIES", "HAIR_BACK", "HAIR_FRONT",
                    "EYES", "MOUTH", "EXTRAS", "FRIEND_KIDS")) \
    + "\n" + function_by_name("butterflySVG") + "\n" + function_by_name("figureSVG") + """
const out = [];
BUTTERFLIES.forEach((b,i)=>out.push({group:'butterfly', name:'butterfly '+(i+1),
  svg:butterflySVG(Object.assign({size:44}, b))}));
FRIEND_KIDS.forEach(f=>out.push({group:f.kind, name:f.name,
  svg:figureSVG(Object.assign({size:52}, f))}));
process.stdout.write(JSON.stringify(out));
"""

js = ROOT / "tools" / "_friends.js"
js.write_text(DRIVER, encoding="utf-8")
r = subprocess.run([str(NODE), str(js)], capture_output=True, text=True)
if r.returncode != 0:
    print(r.stderr[:3000]); sys.exit(1)
friends = json.loads(r.stdout)
print(f"generated {len(friends)} friends")

# --- well-formedness: every generated string must survive a real XML parser ---
bad = 0
for f in friends:
    try:
        etree.fromstring(f["svg"].encode("utf-8"))
    except etree.XMLSyntaxError as e:
        bad += 1
        print(f"  XML FAIL {f['name']}: {e}")
print(f"XML well-formed: {len(friends)-bad}/{len(friends)}")
if bad:
    sys.exit(1)

# --- rasterise into a contact sheet ---
CELL, PAD, GUT = 92, 8, 96
rows = [("butterfly", [f for f in friends if f["group"] == "butterfly"]),
        ("boy", [f for f in friends if f["group"] == "boy"]),
        ("girl", [f for f in friends if f["group"] == "girl"])]
cols = max(len(v) for _, v in rows)
W = GUT + cols * (CELL + PAD) + PAD
H = PAD + sum(CELL + PAD + 18 for _ in rows)
sheet = Image.new("RGB", (W, H), (255, 246, 250))
d = ImageDraw.Draw(sheet)


def font(px, bold=True):
    for name in (("segoeuib.ttf", "arialbd.ttf") if bold else ("segoeui.ttf", "arial.ttf")):
        p = pathlib.Path(r"C:\Windows\Fonts") / name
        if p.exists():
            return ImageFont.truetype(str(p), px)
    return ImageFont.load_default()


y = PAD
for label, items in rows:
    d.text((10, y + CELL // 2), label, font=font(15), fill=(61, 107, 158))
    for i, f in enumerate(items):
        el = etree.fromstring(f["svg"].encode("utf-8"))
        im = svgrender.render(el, scale=2, bg=(255, 255, 255, 255)).convert("RGB")
        im.thumbnail((CELL, CELL), Image.Resampling.LANCZOS)
        x = GUT + PAD + i * (CELL + PAD)
        sheet.paste(im, (x + (CELL - im.width) // 2, y + (CELL - im.height) // 2))
        d.rectangle([x, y, x + CELL, y + CELL], outline=(255, 214, 230))
        d.text((x + 2, y + CELL + 2), f["name"], font=font(11, False), fill=(122, 106, 130))
    y += CELL + PAD + 18

out = ROOT / "tools" / "friends-sheet.png"
sheet.save(out)
print("wrote", out, sheet.size)

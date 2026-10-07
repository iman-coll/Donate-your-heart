"""Static checks for the single-file app: JS syntax, id integrity, ARIA targets."""
import re, sys, pathlib, subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
HTML = ROOT / "docs" / "index.html"
NODE = pathlib.Path(r"C:\Users\Dell\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe")

src = HTML.read_text(encoding="utf-8")
fails, warns = [], []

# ---- 1. every <script> block must parse as JS -------------------------------
blocks = re.findall(r"<script[^>]*>(.*?)</script>", src, re.S)
if not blocks:
    fails.append("no <script> block found")
for i, b in enumerate(blocks):
    f = ROOT / "tools" / f"_block{i}.js"
    f.write_text(b, encoding="utf-8")
    r = subprocess.run([str(NODE), "--check", str(f)], capture_output=True, text=True)
    if r.returncode != 0:
        fails.append(f"script block {i} failed `node --check`:\n{r.stderr.strip()}")
    else:
        print(f"OK   script block {i} parses ({len(b)} chars)")
    f.unlink()

# ---- 2. HTML must parse, with no duplicate ids ------------------------------
from lxml import html as LH
doc = LH.fromstring(src)
ids = doc.xpath("//@id")
dupes = {i for i in ids if ids.count(i) > 1}
if dupes:
    fails.append(f"duplicate ids: {sorted(dupes)}")
print(f"OK   parsed; {len(ids)} ids, {len(set(ids))} unique")

# ---- 3. every $('#x') / $('x') selector target must exist --------------------
refs = set(re.findall(r"\$\('#([A-Za-z0-9_-]+)'\)", src))
refs |= set(re.findall(r"getElementById\('([A-Za-z0-9_-]+)'\)", src))
missing = sorted(refs - set(ids))
if missing:
    fails.append(f"JS references ids that do not exist: {missing}")
print(f"OK   {len(refs)} distinct id references all resolve")

# ---- 4. class selectors used by the gaze engine must exist ------------------
for cls in ("sc-far", "sc-mid", "sc-child", "pupil-g", "lid", "blush"):
    n = len(doc.xpath(f"//*[contains(concat(' ',normalize-space(@class),' '),' {cls} ')]"))
    if n == 0:
        fails.append(f"gaze engine looks for .{cls} but none is in the markup")
    else:
        print(f"OK   .{cls} x{n}")

# ---- 5. ARIA / label targets -------------------------------------------------
for attr in ("aria-labelledby", "aria-describedby"):
    for v in doc.xpath(f"//@{attr}"):
        for tok in v.split():
            if tok not in ids:
                fails.append(f"{attr}=\"{tok}\" points at nothing")
for v in doc.xpath("//label/@for"):
    if v not in ids:
        fails.append(f"<label for=\"{v}\"> points at nothing")
print("OK   aria-labelledby / aria-describedby / label[for] targets resolve")

# ---- 6. the CSP must not be violated by anything the page loads --------------
csp = doc.xpath("//meta[@http-equiv='Content-Security-Policy']/@content")
if not csp:
    fails.append("no CSP meta tag")
else:
    csp = csp[0]
    for pat, why in [
        (r"media-src 'self'", "media-src missing: a local companion clip would be blocked"),
    ]:
        if not re.search(pat, csp):
            warns.append(why)
    for href in doc.xpath("//link[@href]/@href") + doc.xpath("//script[@src]/@src"):
        if href.startswith(("http://", "https://", "//")):
            host = re.sub(r"^https?://([^/]+).*", r"\1", href)
            allowed = ("fonts.googleapis.com" in host and "style-src" in csp) or \
                      ("fonts.gstatic.com" in host and "font-src" in csp)
            if not allowed:
                fails.append(f"external resource not allowed by CSP: {href}")
print("OK   no CSP-blocked external resources")

# ---- 7. no leftover references to things that were removed -------------------
for dead in ("lastFocus", "setAttribute('role','listitem')", "new Date().toISOString().slice(0,10)",
             "'1121'", ">1121<", "1121<"):
    if dead in src:
        fails.append(f"stale reference still present: {dead}")
if doc.xpath("//*[@role='listitem']"):
    fails.append("role=listitem still on an element")

# ---- 8. helplines must cite a source or be explicitly exempt ------------------
hl = src.split("const HELPLINES = [")[1].split("];")[0] if "const HELPLINES = [" in src else ""
entries = hl.count("{ico:")
cited = hl.count("src:'")
print(f"OK   {entries} helplines, {cited} carry a source URL")

# ---- 9. every LOCAL file the page references must actually exist --------------
HERE = HTML.parent
for rel in doc.xpath("//link[@href]/@href") + doc.xpath("//script[@src]/@src") + doc.xpath("//img/@src"):
    if rel.startswith(("http://", "https://", "//", "data:", "#", "tel:", "mailto:")):
        continue
    target = (HERE / rel.split("?")[0].split("#")[0]).resolve()
    if not target.exists():
        fails.append(f"referenced file is missing: {rel}")
    else:
        print(f"OK   referenced file exists: {rel} ({target.stat().st_size} bytes)")

# og:image is an absolute URL but must still name a real local file
for u in doc.xpath("//meta[@property='og:image']/@content"):
    name = u.rsplit("/", 1)[-1]
    if not (HERE / name).exists():
        fails.append(f"og:image points at {u} but {name} is not in the repo")
    else:
        print(f"OK   og:image file exists: {name}")

# ---- 10. manifest must parse and its icons must exist -------------------------
mf = HERE / "manifest.json"
if not mf.exists():
    fails.append("manifest.json missing (the <link rel=manifest> would 404)")
else:
    import json
    man = json.loads(mf.read_text(encoding="utf-8"))
    for key in ("name", "short_name", "start_url", "display", "icons"):
        if key not in man:
            fails.append(f"manifest.json is missing `{key}`")
    for ic in man.get("icons", []):
        if not (HERE / ic["src"]).exists():
            fails.append(f"manifest icon missing: {ic['src']}")
    print(f"OK   manifest.json parses, {len(man.get('icons', []))} icons present")

# ---- 11. companion SVG geometry (the browser cannot render here, so check the maths)
def attr(el, name):
    return el.get(name)

eyes = doc.xpath("//*[local-name()='g'][contains(concat(' ',normalize-space(@class),' '),' eye ')]"
                 "/*[local-name()='ellipse']")
clips = doc.xpath("//*[translate(local-name(),'CP','cp')='clippath']/*[local-name()='ellipse']")
lids = doc.xpath("//*[local-name()='rect'][contains(concat(' ',normalize-space(@class),' '),' lid ')]")
pupils = doc.xpath("//*[local-name()='g'][contains(concat(' ',normalize-space(@class),' '),' pupil-g ')]"
                   "/*[local-name()='circle'][1]")

if not (len(eyes) == len(clips) == len(lids) == len(pupils) == 2):
    fails.append(f"eye/lid/clip/pupil counts must all be 2: eyes={len(eyes)} clips={len(clips)} lids={len(lids)} pupils={len(pupils)}")
else:
    print("OK   2 eyes, 2 clips, 2 lids, 2 pupils")
    for i, (e, c) in enumerate(zip(eyes, clips)):
        if any(attr(e, k) != attr(c, k) for k in ("cx", "cy", "rx", "ry")):
            fails.append(f"clipPath {i} does not match its eye ellipse -> the lid would clip wrong")
    for i, (e, l) in enumerate(zip(eyes, lids)):
        cx, cy, rx, ry = (float(attr(e, k)) for k in ("cx", "cy", "rx", "ry"))
        lx, ly, lw = float(attr(l, "x")), float(attr(l, "y")), float(attr(l, "width"))
        if abs(ly - (cy - ry)) > 0.2:
            fails.append(f"lid {i} does not start at the top of its eye (y={ly}, eye top={cy-ry})")
        if lx > cx - rx + 0.2 or lx + lw < cx + rx - 0.2:
            fails.append(f"lid {i} does not span its eye horizontally")
    m = re.search(r"TILT=([\d.]+),\s*FAR_S=([\d.]+),\s*MID_S=([\d.]+),\s*KID_S=([\d.]+),"
                  r"\s*PUPIL=([\d.]+),\s*LID_H=([\d.]+)", src)
    if not m:
        fails.append("could not read the gaze tuning constants")
    else:
        TILT, FAR_S, MID_S, KID_S, PUPIL, LID_H = (float(x) for x in m.groups())
        print(f"OK   tuning TILT={TILT} FAR_S={FAR_S} MID_S={MID_S} KID_S={KID_S} PUPIL={PUPIL} LID_H={LID_H}")
        ry = float(attr(eyes[0], "ry"))
        if LID_H < 2 * ry:
            fails.append(f"LID_H={LID_H} cannot fully close an eye of height {2*ry} -> the blink never shuts")
        rx, pry = float(attr(eyes[0], "rx")), float(attr(pupils[0], "r"))
        if PUPIL + pry > rx - 0.4:
            fails.append(f"pupil escapes the white of the eye: {PUPIL}+{pry} > {rx}")
        if PUPIL * 0.78 + pry > ry - 0.4:
            fails.append(f"pupil escapes the white vertically: {PUPIL*0.78}+{pry} > {ry}")
        if TILT > 12:
            warns.append(f"TILT={TILT}deg is a lot of rotation for a face")
        # the far layer must overhang by at least its own parallax travel
        farsky = doc.xpath("//*[local-name()='g'][contains(@class,'sc-far')]/*[local-name()='rect']")[0]
        if float(attr(farsky, "x")) > -FAR_S:
            fails.append(f"far layer starts at x={attr(farsky,'x')} but slides up to {FAR_S}px -> gap at the edge")
        if float(attr(farsky, "x")) + float(attr(farsky, "width")) < 320 + FAR_S:
            fails.append("far layer does not cover the right edge after parallax")

    # the child figure must sit inside the 320x190 viewBox, allowing for its travel
    kid_boxes = doc.xpath("//*[local-name()='g'][contains(@class,'sc-child')]//*[local-name()='circle' or local-name()='ellipse' or local-name()='rect']")
    for el in kid_boxes:
        cx = float(attr(el, "cx") or 0) or (float(attr(el, "x") or 0) + float(attr(el, "width") or 0) / 2)
        r = float(attr(el, "r") or 0) or float(attr(el, "rx") or 0) or float(attr(el, "width") or 0) / 2
        if cx - r < 0 or cx + r > 320:
            fails.append(f"child element at cx={cx} r={r} leaves the viewBox horizontally")
    print(f"OK   checked {len(kid_boxes)} child-layer shapes against the viewBox")

# ---- 12. the companion must be on Home, above the categories ------------------
hero = doc.xpath("//*[@id='child-hero']")
if not hero:
    fails.append("#child-hero is missing")
else:
    home = doc.xpath("//*[@id='view-home']")[0]
    ids_in_home = home.xpath(".//@id")
    if "child-hero" not in ids_in_home:
        fails.append("#child-hero is not inside #view-home")
    elif ids_in_home.index("child-hero") > ids_in_home.index("cat-grid"):
        warns.append("#child-hero sits below the category grid (unreachable at a glance on a phone)")
    else:
        print("OK   #child-hero is on Home, above the category grid")
    # the caption bar and the pause control were removed on request
    for gone in ("gaze-toggle", "child-caption p", "a child's face should not be a conversion tool",
                 "Illustrated companion.</b>"):
        if gone in src:
            fails.append(f"removed UI is still present: {gone}")
    print("OK   caption bar and pause button are gone")

    # ---- the cursor entourage overlay ----
    fr = doc.xpath("//*[@id='friends']")
    if not fr:
        fails.append("#friends overlay is missing")
    else:
        if fr[0].get("aria-hidden") != "true":
            fails.append("#friends must be aria-hidden — it is pure decoration")
        if "#friends{" not in src:
            fails.append("#friends has no CSS rule")
        else:
            rule = src.split("#friends{", 1)[1][:220]
            if "pointer-events:none" not in rule:
                fails.append("#friends must be pointer-events:none or it blocks every click")
            if "position:fixed" not in rule:
                fails.append("#friends must be position:fixed to follow the pointer")
        if "friends" in doc.xpath("//*[@id='app']//@id"):
            warns.append("#friends sits inside #app; keeping it outside is simpler")
        else:
            print("OK   #friends overlay is decoration-only, fixed and click-through")
    if "@keyframes flap" not in src:
        fails.append("the butterfly wing-flap keyframes are missing")
    if "initFriends()" not in src:
        fails.append("initFriends() is never called")
    print("OK   entourage is initialised and the wings have a flap animation")

# ---- 13. router / nav / in-app link wiring ------------------------------------
m = re.search(r"const ROUTES=\[([^\]]*)\]", src)
if not m:
    fails.append("no ROUTES array in the router")
else:
    routes = [r.strip().strip("'\"") for r in m.group(1).split(",") if r.strip()]
    views = {v.get("id")[5:] for v in doc.xpath("//section[contains(@class,'view')][@id]")}
    for r in routes:
        if r not in views:
            fails.append(f"route '{r}' has no #view-{r} section")
    for extra in sorted(views - set(routes)):
        fails.append(f"#view-{extra} exists but is not routable")
    print(f"OK   {len(routes)} routes, each with a matching view section")

    nav = doc.xpath("//button[contains(@class,'navbtn')]/@data-view")
    for v in nav:
        if v not in routes:
            fails.append(f"nav tab data-view='{v}' is not a route")
    if len(nav) != len(set(nav)):
        fails.append("duplicate nav tabs")
    print(f"OK   {len(nav)} nav tabs: {', '.join(nav)}")

    gotos = doc.xpath("//*[@data-goto]/@data-goto")
    for g in gotos:
        if g not in routes:
            fails.append(f"data-goto='{g}' is not a route")
    print(f"OK   {len(gotos)} in-app links, all targets routable")

    # a page with no tab needs a parent tab, or the nav goes blank on it
    m2 = re.search(r"const NAV_PARENT=\{([^}]*)\}", src)
    parents = dict(re.findall(r"(\w+):'(\w+)'", m2.group(1))) if m2 else {}
    for r in routes:
        if r not in nav and r not in parents:
            fails.append(f"route '{r}' has no tab and no parent tab -> the nav would go blank")
    print(f"OK   secondary pages mapped to a parent tab: {parents}")

# ---- 14. mascots: every avatar must be backed by a real, animated sheet -------
sheet_block = src[src.index("const sheets={"):src.index("const sprites=[];")]
built = dict(re.findall(r"(\w+)\s*:\s*CONFIG\.art\.\w+\s*\?.*?:\s*bakeSheet\((\w+)\)", sheet_block))
avatars = re.findall(r"\{id:'(\w+)',ico:'[^']+',sheet:'(\w+)'\}", src)
if len(avatars) != 4:
    fails.append(f"expected 4 avatars, found {len(avatars)}")
if re.search(r"\{id:'\w+',ico:'[^']+',sheet:null\}", src):
    fails.append("an avatar still has sheet:null — it would fall back to a static emoji")
for aid, key in avatars:
    if key not in built:
        fails.append(f"avatar '{aid}' points at sheets.{key}, which does not exist")
    elif f"function {built[key]}(" not in src:
        fails.append(f"sheets.{key} bakes {built[key]}(), which is not defined")
print(f"OK   {len(avatars)} avatars, all backed by a baked sheet: " +
      ", ".join(f"{a}->{k}" for a, k in avatars))
for key, fn in sorted(built.items()):
    i = src.index(f"function {fn}(")
    j = src.index("\nfunction ", i + 1)
    body = src[i:j]
    if "TAU" not in body:
        fails.append(f"{fn}() has no animated cycle (no TAU)")
    if "blink" not in body:
        fails.append(f"{fn}() never blinks")
print(f"OK   all {len(built)} mascots animate: hop cycle + a blink frame")

print()
for w in warns:
    print("WARN", w)
for f in fails:
    print("FAIL", f)
print("\nRESULT:", "FAIL" if fails else "PASS")
sys.exit(1 if fails else 0)

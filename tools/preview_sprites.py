"""Render the four baked mascot sheets so a human can look at them.

The mascots are drawn with Canvas2D in JS and the browser cannot run here, so this
runs the REAL `drawBear`/`drawBunny`/`drawCastle`/`drawChick` code in Node against a
small Canvas2D shim that records flattened paths, then rasterises those with Pillow.

It is an approximation of the canvas renderer (fills are flattened to polygons, round
caps are approximated), not a reference implementation. Its job is to answer "does the
chick look like a chick, and does it animate like the other three".
"""
import json, pathlib, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
NODE = pathlib.Path(r"C:\Users\Dell\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe")
APP = ROOT / "docs" / "index.html"

body = re.search(r"<script[^>]*>(.*?)</script>", APP.read_text(encoding="utf-8"), re.S).group(1)
region = body[body.index("if(!CanvasRenderingContext2D.prototype.roundRect){"):body.index("const sprites=[];")]

SHIM = r"""
const CANVASES = [];
function M(){ return [1,0,0,1,0,0]; }
function mul(m,n){ return [ m[0]*n[0]+m[2]*n[1], m[1]*n[0]+m[3]*n[1],
                           m[0]*n[2]+m[2]*n[3], m[1]*n[2]+m[3]*n[3],
                           m[0]*n[4]+m[2]*n[5]+m[4], m[1]*n[4]+m[3]*n[5]+m[5] ]; }
function ap(m,x,y){ return [ m[0]*x+m[2]*y+m[4], m[1]*x+m[3]*y+m[5] ]; }

class Ctx {
  constructor(){ this.stack=[]; this.ops=[]; this.m=M();
    this.fillStyle='#000'; this.strokeStyle='#000'; this.lineWidth=1; this.lineCap='butt';
    this.path=[]; this.cur=null; }
  save(){ this.stack.push({m:this.m.slice(), f:this.fillStyle, s:this.strokeStyle,
                           w:this.lineWidth, c:this.lineCap}); }
  restore(){ const s=this.stack.pop(); if(s){ this.m=s.m; this.fillStyle=s.f;
    this.strokeStyle=s.s; this.lineWidth=s.w; this.lineCap=s.c; } }
  translate(x,y){ this.m=mul(this.m,[1,0,0,1,x,y]); }
  rotate(a){ const c=Math.cos(a), s=Math.sin(a); this.m=mul(this.m,[c,s,-s,c,0,0]); }
  beginPath(){ this.path=[]; this.cur=null; }
  _push(p){ if(!this.cur){ this.cur=[p]; this.path.push(this.cur); } else this.cur.push(p); }
  moveTo(x,y){ this.cur=null; this._push(ap(this.m,x,y)); }
  lineTo(x,y){ if(!this.cur) return this.moveTo(x,y); this._push(ap(this.m,x,y)); }
  closePath(){ if(this.cur) this.cur.closed=true; }
  bezierCurveTo(x1,y1,x2,y2,x,y){
    const p0 = this.cur ? this.cur[this.cur.length-1] : ap(this.m,0,0);
    const P1=ap(this.m,x1,y1), P2=ap(this.m,x2,y2), P3=ap(this.m,x,y);
    for(let i=1;i<=18;i++){ const t=i/18, u=1-t;
      this._push([ u*u*u*p0[0]+3*u*u*t*P1[0]+3*u*t*t*P2[0]+t*t*t*P3[0],
                   u*u*u*p0[1]+3*u*u*t*P1[1]+3*u*t*t*P2[1]+t*t*t*P3[1] ]); }
  }
  _ellipse(cx,cy,rx,ry,a1,a2){
    this.cur=null; const N=40;
    for(let i=0;i<=N;i++){ const a=a1+(a2-a1)*i/N;
      this._push(ap(this.m, cx+Math.cos(a)*rx, cy+Math.sin(a)*ry)); }
    if(this.cur) this.cur.closed=true;
  }
  ellipse(cx,cy,rx,ry,rot,a1,a2){ this._ellipse(cx,cy,rx,ry,a1,a2); }
  arc(cx,cy,r,a1,a2,acw){
    if(acw===undefined) acw=false;
    if(!acw && a2<a1) a2+=2*Math.PI;
    if(acw && a2>a1) a2-=2*Math.PI;
    this._ellipse(cx,cy,r,r,a1,a2);
  }
  roundRect(x,y,w,h,r){
    if(typeof r==='number') r=[r,r,r,r];
    const tl=r[0],tr=r[1],br=r[2],bl=r[3];
    this.cur=null;
    const P=(px,py)=>this._push(ap(this.m,px,py));
    const Q=(px,py,rad,a0)=>{ for(let i=1;i<=7;i++){ const a=a0+(Math.PI/2)*i/7;
      P(px+Math.cos(a)*rad, py+Math.sin(a)*rad); } };
    P(x+tl,y); P(x+w-tr,y); Q(x+w-tr,y+tr,tr,-Math.PI/2);
    P(x+w,y+h-br); Q(x+w-br,y+h-br,br,0);
    P(x+bl,y+h); Q(x+bl,y+h-bl,bl,Math.PI/2);
    P(x,y+tl); Q(x+tl,y+tl,tl,Math.PI);
    if(this.cur) this.cur.closed=true;
  }
  fillRect(x,y,w,h){
    this.ops.push({t:'fill', c:this.fillStyle,
      sub:[[ap(this.m,x,y),ap(this.m,x+w,y),ap(this.m,x+w,y+h),ap(this.m,x,y+h)]]});
  }
  fill(){ if(this.path.length) this.ops.push({t:'fill', c:this.fillStyle, sub:this.path.map(s=>s.slice())}); }
  stroke(){ if(this.path.length) this.ops.push({t:'stroke', c:this.strokeStyle,
    w:this.lineWidth, cap:this.lineCap, sub:this.path.map(s=>s.slice())}); }
}

class FakeCanvas {
  constructor(){ this.width=0; this.height=0; this._c=new Ctx(); CANVASES.push(this); }
  getContext(){ return this._c; }
  toDataURL(){ return ''; }
}
globalThis.CanvasRenderingContext2D = function(){};
globalThis.CanvasRenderingContext2D.prototype.roundRect = function(){};   // skip the app's polyfill
globalThis.document = { createElement: () => new FakeCanvas() };
const CONFIG = { art: { bear:'', bunny:'', castle:'', chick:'' } };
"""

TAIL = "\nprocess.stdout.write(JSON.stringify(CANVASES.map(c=>({w:c.width,h:c.height,ops:c._c.ops}))));\n"

js = ROOT / "tools" / "_sprites.js"
js.write_text(SHIM + region + TAIL, encoding="utf-8")
r = subprocess.run([str(NODE), str(js)], capture_output=True, text=True)
if r.returncode != 0:
    print(r.stderr[:3000]); sys.exit(1)
canvases = json.loads(r.stdout)
names = ["bear", "bunny", "castle", "chick"]
print("recorded:", [(n, c["w"], c["h"], len(c["ops"])) for n, c in zip(names, canvases)])


def parse_colour(s):
    s = s.strip()
    m = re.match(r"rgba?\(([^)]+)\)", s)
    if m:
        p = [x.strip() for x in m.group(1).split(",")]
        r_, g_, b_ = (int(float(p[i])) for i in range(3))
        a = int(float(p[3]) * 255) if len(p) > 3 else 255
        return (r_, g_, b_, a)
    s = s.lstrip("#")
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), 255)


def draw_strip(canvas):
    w, h = canvas["w"], canvas["h"]
    base = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    for op in canvas["ops"]:
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        col = parse_colour(op["c"])
        if op["t"] == "fill":
            for sub in op["sub"]:
                if len(sub) > 2:
                    d.polygon([tuple(p) for p in sub], fill=col)
        else:
            lw = max(1, int(round(op.get("w", 1))))
            for sub in op["sub"]:
                pts = [tuple(p) for p in sub]
                if len(pts) > 1:
                    d.line(pts, fill=col, width=lw, joint="curve")
                if op.get("cap") == "round":
                    for p in (pts[0], pts[-1]):
                        if len(pts) > 1:
                            d.ellipse([p[0] - lw / 2, p[1] - lw / 2, p[0] + lw / 2, p[1] + lw / 2], fill=col)
        base = Image.alpha_composite(base, layer)
    return base.convert("RGB")


def font(px):
    for name in ("segoeuib.ttf", "arialbd.ttf"):
        p = pathlib.Path(r"C:\Windows\Fonts") / name
        if p.exists():
            return ImageFont.truetype(str(p), px)
    return ImageFont.load_default()


CELL, GUTTER, PAD = 84, 74, 6
cols = max(c["w"] // 160 for c in canvases)
sheet = Image.new("RGB", (GUTTER + cols * (CELL + PAD) + PAD,
                          4 * (CELL + PAD) + PAD), (255, 246, 250))
draw = ImageDraw.Draw(sheet)
for row, (name, canvas) in enumerate(zip(names, canvases)):
    strip = draw_strip(canvas)
    y = PAD + row * (CELL + PAD)
    draw.text((8, y + CELL // 2 - 12), name, font=font(17), fill=(61, 107, 158))
    for i in range(cols):
        frame = strip.crop((i * 160, 0, i * 160 + 160, 160)).resize((CELL, CELL), Image.Resampling.LANCZOS)
        sheet.paste(frame, (GUTTER + PAD + i * (CELL + PAD), y))
        draw.rectangle([GUTTER + PAD + i * (CELL + PAD), y,
                        GUTTER + PAD + i * (CELL + PAD) + CELL, y + CELL], outline=(255, 214, 230))

out = ROOT / "tools" / "sprite-sheet.png"
sheet.save(out)
print("wrote", out, sheet.size)

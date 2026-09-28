"""Convert a fixed-size HTML layout into an editable Illustrator document (vectors, real text, embedded photos).

    python tools/html2ai.py layout.html out.ai --w 600 --h 800 [--root .canvas] [--png out.png]

How it works
1. Playwright (Chromium) opens the page at w x h CSS px and measures every element under --root.
2. Each element's box becomes vector art on its own layer, bottom to top in paint order:
     background-color / linear-gradient  -> rectangle or rounded rectangle (border-radius) with that fill
     border (uniform)                     -> stroke on the same shape; per-side borders -> separate lines
     box-shadow (outer)                   -> live drop shadow effect (AI.dropShadow)
     opacity                              -> item opacity
     <img>                                -> PNG of exactly what the browser shows (object-fit / crop), embedded
     inline <svg>                         -> imported as vector paths (groupItems.createFromFile)
3. Text becomes real text frames, one per rendered line, with font family / weight / italic / size / color /
   letter-spacing (as tracking) / opacity, placed on the browser's baseline. writing-mode vertical-* -> vertical type.
4. The script runs through lib/ai_run.py (COM, no dialogs); out.ai (+ optional PNG) are saved.
1 CSS px = 1 pt, so a 600 x 800 layout gives a 600 x 800 pt artboard (exports at 100% are 600 x 800 px).
Fonts must be installed locally; families Illustrator cannot find are reported and fall back to ArialMT.
"""
import argparse
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL / "lib"))
sys.stdout.reconfigure(encoding="utf-8")
from ai_run import run_js  # noqa: E402
from ailib_loader import library  # noqa: E402

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("html")
ap.add_argument("out")
ap.add_argument("--w", type=int, required=True)
ap.add_argument("--h", type=int, required=True)
ap.add_argument("--root", default=".canvas")
ap.add_argument("--png", help="also export the artboard as PNG")
ap.add_argument("--keep-open", action="store_true", help="leave the document open in Illustrator")
a = ap.parse_args()
html, out = Path(a.html).resolve(), Path(a.out).resolve()
work = out.with_suffix("")
work.mkdir(parents=True, exist_ok=True)
for f in work.glob("*"):
    f.unlink()

MEASURE_JS = r"""(sel) => {
  const root = document.querySelector(sel) || document.body;
  root.setAttribute('data-ai-root', '');
  const R0 = root.getBoundingClientRect();
  const ctx = document.createElement('canvas').getContext('2d');
  const boxes = [], texts = [], imgs = [], svgs = [];
  let order = 0;
  const px = v => parseFloat(v) || 0;
  function paint(el, cs, r) {
    const bw = ['Top', 'Right', 'Bottom', 'Left'].map(s => px(cs['border' + s + 'Width']));
    const bc = ['Top', 'Right', 'Bottom', 'Left'].map(s => cs['border' + s + 'Color']);
    const bs = ['Top', 'Right', 'Bottom', 'Left'].map(s => cs['border' + s + 'Style']);
    const bg = cs.backgroundColor, gi = cs.backgroundImage;
    const hasBg = bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent';
    const hasGrad = gi && gi.indexOf('linear-gradient') === 0;
    const hasBorder = bw.some((w, i) => w > 0 && bs[i] !== 'none' && bc[i] !== 'rgba(0, 0, 0, 0)');
    const sh = cs.boxShadow && cs.boxShadow !== 'none' ? cs.boxShadow : null;
    if (!hasBg && !hasGrad && !hasBorder && !sh) return;
    boxes.push({o: order++, x: r.left - R0.left, y: r.top - R0.top, w: r.width, h: r.height, bg: hasBg ? bg : null, grad: hasGrad ? gi : null,
                bw, bc, bs, radius: px(cs.borderTopLeftRadius), shadow: sh, opacity: +cs.opacity, tag: el.tagName.toLowerCase(), cls: el.className && el.className.baseVal === undefined ? el.className : ''});
  }
  const all = [root, ...root.querySelectorAll('*')];
  for (const el of all) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    if (el.closest('svg') && el.tagName.toLowerCase() !== 'svg') continue;
    const r = el.getBoundingClientRect();
    if (el.tagName.toLowerCase() === 'svg') { el.dataset.aiSvg = svgs.length; svgs.push({o: order++, i: svgs.length, x: r.left - R0.left, y: r.top - R0.top, w: r.width, h: r.height, src: el.outerHTML}); continue; }
    if (el !== root || true) paint(el, cs, r);
    if (el.tagName.toLowerCase() === 'img') { el.dataset.aiImg = imgs.length; imgs.push({o: order++, i: imgs.length, x: r.left - R0.left, y: r.top - R0.top, w: r.width, h: r.height, opacity: +cs.opacity}); continue; }
    const nodes = [...el.childNodes].filter(n => n.nodeType === 3 && n.textContent.trim());
    if (!nodes.length) continue;
    const vertical = cs.writingMode !== 'horizontal-tb';
    ctx.font = `${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
    const mt = ctx.measureText('Hg'), asc = mt.fontBoundingBoxAscent;
    for (const n of nodes) {
      const lines = {}, s = n.textContent;
      for (let i = 0; i < s.length; i++) {
        const rg = document.createRange(); rg.setStart(n, i); rg.setEnd(n, i + 1);
        const rc = [...rg.getClientRects()].filter(x => x.width > 0 && x.height > 0)[0];
        if (!rc) continue;
        const k = vertical ? Math.round(rc.left) : Math.round(rc.top);
        const L = (lines[k] = lines[k] || {top: rc.top, left: rc.left, right: rc.right, bottom: rc.bottom, s: ''});
        L.s += s[i]; L.left = Math.min(L.left, rc.left); L.top = Math.min(L.top, rc.top); L.right = Math.max(L.right, rc.right); L.bottom = Math.max(L.bottom, rc.bottom);
      }
      for (const L of Object.values(lines)) {
        let t = L.s.replace(/\s+/g, ' ').trim();
        if (!t) continue;
        if (cs.textTransform === 'uppercase') t = t.toUpperCase();
        if (cs.textTransform === 'lowercase') t = t.toLowerCase();
        texts.push({o: order++, t, vertical, x: L.left - R0.left, y: L.top - R0.top, w: L.right - L.left, h: L.bottom - L.top, base: L.top - R0.top + asc,
                    family: cs.fontFamily.split(',')[0].replace(/["']/g, '').trim(), weight: +cs.fontWeight, italic: cs.fontStyle === 'italic',
                    size: parseFloat(cs.fontSize), color: cs.color, ls: cs.letterSpacing === 'normal' ? 0 : parseFloat(cs.letterSpacing),
                    opacity: +cs.opacity, align: cs.textAlign});
      }
    }
  }
  return {boxes, texts, imgs, svgs};
}"""

with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page(viewport={"width": a.w, "height": a.h})
    pg.goto(html.as_uri())
    pg.wait_for_load_state("networkidle")
    pg.evaluate("document.fonts.ready")
    m = pg.evaluate(MEASURE_JS, a.root)
    clip = {"x": 0, "y": 0, "width": a.w, "height": a.h}
    pg.screenshot(path=str(work / "_reference.png"), clip=clip)
    for im in m["imgs"]:
        h = pg.add_style_tag(content="[data-ai-root] *, [data-ai-root] {visibility:hidden !important; background:transparent !important} "
                                     f"[data-ai-img='{im['i']}']{{visibility:visible !important}} html, body {{background:transparent !important}}")
        box = {"x": max(0, im["x"]), "y": max(0, im["y"]), "width": min(im["w"], a.w - max(0, im["x"])), "height": min(im["h"], a.h - max(0, im["y"]))}
        pg.screenshot(path=str(work / f"img{im['i']}.png"), clip=box, omit_background=True)
        im.update({"x": box["x"], "y": box["y"], "w": box["width"], "h": box["height"]})
        h.evaluate("e => e.remove()")
    for sv in m["svgs"]:
        src = sv["src"]
        if "xmlns=" not in src:
            src = src.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
        (work / f"svg{sv['i']}.svg").write_text(src, encoding="utf-8")
    b.close()


def rgba(s):
    if not s:
        return None
    v = [float(x) for x in s[s.index("(") + 1:s.index(")")].replace("/", ",").split(",") if x.strip()]
    return [round(v[0]), round(v[1]), round(v[2]), v[3] if len(v) > 3 else 1.0]


def grad(s):
    """linear-gradient(90deg, rgb(..) 0%, rgb(..) 100%) -> {angle, stops}"""
    import re
    inner = s[s.index("(") + 1:s.rindex(")")]
    parts, depth, cur = [], 0, ""
    for ch in inner:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur.strip())
            cur = ""
        else:
            cur += ch
    parts.append(cur.strip())
    ang = 180.0
    if parts and re.match(r"^-?[\d.]+deg$", parts[0]):
        ang = float(parts.pop(0)[:-3])
    elif parts and parts[0].startswith("to "):
        ang = {"to top": 0, "to right": 90, "to bottom": 180, "to left": 270}.get(parts.pop(0), 180)
    stops = []
    for i, p in enumerate(parts):
        m2 = re.match(r"(rgba?\([^)]*\))\s*([\d.]+%)?", p)
        if not m2:
            continue
        pos = float(m2.group(2)[:-1]) / 100 if m2.group(2) else i / max(1, len(parts) - 1)
        stops.append([pos, rgba(m2.group(1))])
    return {"angle": (90 - ang) % 360, "stops": stops}   # CSS 0deg = up, clockwise; Illustrator 0 = right, counter-clockwise


def shadow(s):
    import re
    m2 = re.match(r"(rgba?\([^)]*\))\s+(-?[\d.]+)px\s+(-?[\d.]+)px\s*([\d.]+)?px?", s)
    if not m2 or " inset" in s:
        return None
    c = rgba(m2.group(1))
    return {"x": float(m2.group(2)), "y": float(m2.group(3)), "blur": float(m2.group(4) or 0) / 2, "opacity": c[3], "color": c[:3]}


items = []
for bx in m["boxes"]:
    items.append({"k": "box", "o": bx["o"], "x": bx["x"], "y": bx["y"], "w": bx["w"], "h": bx["h"], "bg": rgba(bx["bg"]),
                  "grad": grad(bx["grad"]) if bx["grad"] else None, "bw": bx["bw"], "bc": [rgba(c) for c in bx["bc"]], "bs": bx["bs"],
                  "r": bx["radius"], "shadow": shadow(bx["shadow"]) if bx["shadow"] else None, "op": bx["opacity"], "name": (bx["cls"] or bx["tag"])[:40]})
for im in m["imgs"]:
    items.append({"k": "img", "o": im["o"], "x": im["x"], "y": im["y"], "w": im["w"], "h": im["h"], "f": str(work / f"img{im['i']}.png"), "op": im["opacity"]})
for sv in m["svgs"]:
    items.append({"k": "svg", "o": sv["o"], "x": sv["x"], "y": sv["y"], "w": sv["w"], "h": sv["h"], "f": str(work / f"svg{sv['i']}.svg")})
for t in m["texts"]:
    items.append({"k": "text", "o": t["o"], **t, "color": rgba(t["color"]), "tracking": round(t["ls"] / t["size"] * 1000) if t["size"] else 0})
items.sort(key=lambda x: x["o"])
(work / "layout.json").write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")

JSX = library() + r"""
var IT = __ITEMS__, OUT = __OUT__, PNGOUT = __PNG__, W = __W__, H = __H__;
var D = AI.newDoc(W, H, 'html2ai', {units: 'px'});
var L = {shapes: AI.layer('Shapes'), images: AI.layer('Images'), text: AI.layer('Text')};
L.images.zOrder(ZOrderMethod.BRINGTOFRONT); L.text.zOrder(ZOrderMethod.BRINGTOFRONT);
try { D.layers.getByName('Layer 1').remove(); } catch (e) {} try { D.layers.getByName('圖層 1').remove(); } catch (e) {}
var WEIGHT = {100: ['Thin', 'Hairline'], 200: ['ExtraLight', 'UltraLight'], 300: ['Light'], 400: ['Regular', 'Roman', 'Book', 'Normal', ''], 500: ['Medium'],
  600: ['SemiBold', 'DemiBold'], 700: ['Bold'], 800: ['ExtraBold', 'Heavy'], 900: ['Black', 'Heavy']};
var fontCache = {}, missing = {};
function pickFont(fam, weight, italic) {
  var key = fam + '|' + weight + '|' + italic; if (fontCache[key] !== undefined) return fontCache[key];
  var want = fam.toLowerCase().replace(/\s/g, ''), best = null, bestScore = -1;
  for (var i = 0; i < app.textFonts.length; i++) {
    var f = app.textFonts[i], fm = f.family.toLowerCase().replace(/\s/g, '');
    if (fm != want && f.name.toLowerCase().replace(/[\s-]/g, '').indexOf(want) != 0) continue;
    var st = f.style.toLowerCase(), sc = 1, wn = WEIGHT[Math.round(weight / 100) * 100] || ['Regular'];
    for (var k = 0; k < wn.length; k++) if (wn[k] && st.indexOf(wn[k].toLowerCase()) >= 0) sc += 4;
    if (weight == 400 && (st == 'regular' || st == 'roman' || st == 'book' || st == 'italic' || st == 'oblique')) sc += 3;
    if (italic == (st.indexOf('italic') >= 0 || st.indexOf('oblique') >= 0)) sc += 10;      // slant outranks weight
    if (sc > bestScore) { bestScore = sc; best = f; }
  }
  if (!best) { missing[fam] = 1; best = app.textFonts.getByName('ArialMT'); }
  return (fontCache[key] = best);
}
var n = {box: 0, img: 0, svg: 0, text: 0};
for (var i = 0; i < IT.length; i++) {
  var t = IT[i];
  if (t.k == 'box') {
    var fill = t.grad ? AI.gradient(t.grad.stops.map ? t.grad.stops : t.grad.stops, {angle: t.grad.angle}) : (t.bg && t.bg[3] > 0 ? AI.rgb(t.bg[0], t.bg[1], t.bg[2]) : null);
    var uni = t.bw[0] == t.bw[1] && t.bw[1] == t.bw[2] && t.bw[2] == t.bw[3] && t.bw[0] > 0 && t.bs[0] != 'none';
    var sh = t.r > 0 ? AI.roundRect(t.x + (uni ? t.bw[0] / 2 : 0), t.y + (uni ? t.bw[0] / 2 : 0), t.w - (uni ? t.bw[0] : 0), t.h - (uni ? t.bw[0] : 0), t.r)
                     : AI.rect(t.x + (uni ? t.bw[0] / 2 : 0), t.y + (uni ? t.bw[0] / 2 : 0), t.w - (uni ? t.bw[0] : 0), t.h - (uni ? t.bw[0] : 0));
    AI.style(sh, {fill: fill, stroke: uni ? [t.bc[0][0], t.bc[0][1], t.bc[0][2]] : null, strokeWidth: uni ? t.bw[0] : 0, name: t.name});
    if (uni && t.bs[0] == 'dashed') sh.strokeDashes = [t.bw[0] * 3, t.bw[0] * 2];
    if (uni && t.bs[0] == 'dotted') { sh.strokeDashes = [0, t.bw[0] * 2]; sh.strokeCap = StrokeCap.ROUNDENDCAP; }
    if (t.bg && t.bg[3] < 1 && !t.grad) sh.opacity = t.bg[3] * 100;
    if (t.op < 1) sh.opacity = sh.opacity * t.op;
    sh.move(L.shapes, ElementPlacement.PLACEATBEGINNING);
    if (!uni) {                                                    // per-side borders as lines
      var sides = [[0, t.x, t.y + t.bw[0] / 2, t.x + t.w, t.y + t.bw[0] / 2], [1, t.x + t.w - t.bw[1] / 2, t.y, t.x + t.w - t.bw[1] / 2, t.y + t.h],
                   [2, t.x, t.y + t.h - t.bw[2] / 2, t.x + t.w, t.y + t.h - t.bw[2] / 2], [3, t.x + t.bw[3] / 2, t.y, t.x + t.bw[3] / 2, t.y + t.h]];
      for (var s = 0; s < 4; s++) { var k = sides[s][0]; if (t.bw[k] > 0 && t.bs[k] != 'none' && t.bc[k][3] > 0) {
        var ln = AI.line(sides[s][1], sides[s][2], sides[s][3], sides[s][4], {stroke: [t.bc[k][0], t.bc[k][1], t.bc[k][2]], strokeWidth: t.bw[k], name: t.name + ' border'});
        if (t.bs[k] == 'dashed') ln.strokeDashes = [t.bw[k] * 3, t.bw[k] * 2];
        if (t.bs[k] == 'dotted') { ln.strokeDashes = [0, t.bw[k] * 2]; ln.strokeCap = StrokeCap.ROUNDENDCAP; }
        ln.move(L.shapes, ElementPlacement.PLACEATBEGINNING); } }
      if (!fill) sh.remove();
    }
    if (t.shadow) try { AI.dropShadow(sh, {x: t.shadow.x, y: t.shadow.y, blur: t.shadow.blur, opacity: t.shadow.opacity}); } catch (e) {}
    n.box++;
  } else if (t.k == 'img') {
    var p = AI.place(new File(t.f), t.x, t.y, {w: t.w, h: t.h, embed: true}); p.move(L.images, ElementPlacement.PLACEATBEGINNING);
    AI.moveTo(p, t.x, t.y); if (t.op < 1) p.opacity = t.op * 100; p.name = 'image ' + (n.img + 1); n.img++;
  } else if (t.k == 'svg') {
    var g = D.groupItems.createFromFile(new File(t.f)); g.move(L.shapes, ElementPlacement.PLACEATBEGINNING);
    var b = AI.box(g); if (b.w > 0 && b.h > 0) { g.resize(t.w / b.w * 100, t.h / b.h * 100, true, true, true, true, 100, Transformation.TOPLEFT); } AI.moveTo(g, t.x, t.y); g.name = 'svg ' + (n.svg + 1); n.svg++;
  } else if (t.k == 'text') {
    var f = pickFont(t.family, t.weight, t.italic);
    var tf = D.textFrames.pointText(AI.pt(t.x, t.base)); tf.contents = t.t;
    var ca = tf.textRange.characterAttributes; ca.textFont = f; ca.size = t.size; ca.fillColor = AI.rgb(t.color[0], t.color[1], t.color[2]); ca.tracking = t.tracking;
    if (t.vertical) { tf.orientation = TextOrientation.VERTICAL; AI.moveTo(tf, t.x, t.y); }
    if (t.color[3] < 1) tf.opacity = t.color[3] * 100; if (t.opacity < 1) tf.opacity = tf.opacity * t.opacity;
    tf.move(L.text, ElementPlacement.PLACEATBEGINNING); tf.name = t.t.substr(0, 30); n.text++;
  }
}
L.images.zOrder(ZOrderMethod.SENDTOBACK); L.shapes.zOrder(ZOrderMethod.SENDTOBACK);
var ms = []; for (var k2 in missing) ms.push(k2);
AI.saveAI(OUT); if (PNGOUT) AI.png(PNGOUT);
var res = {boxes: n.box, images: n.img, svgs: n.svg, texts: n.text, missing: ms, items: D.pageItems.length};
if (!__KEEP__) D.close(SaveOptions.DONOTSAVECHANGES);
J(res);
"""
js = (JSX.replace("__ITEMS__", json.dumps(items, ensure_ascii=False)).replace("__OUT__", json.dumps(out.as_posix()))
      .replace("__PNG__", json.dumps(Path(a.png).resolve().as_posix() if a.png else "")).replace("__W__", str(a.w)).replace("__H__", str(a.h))
      .replace("__KEEP__", "true" if a.keep_open else "false"))
res = json.loads(run_js(js, dialog="esc", timeout=600))
print(f"{out}: {res['boxes']} shapes, {res['images']} images, {res['svgs']} svg, {res['texts']} text lines "
      f"({res['items']} items); missing fonts: {', '.join(res['missing']) or 'none'}")

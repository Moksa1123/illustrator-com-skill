"""Industry-standard logo delivery package, produced in Illustrator from a finished logo kit.

Input: a kit folder with RGB masters (<name>.ai) per layout x tone (one per brand, described by a JSON config).
Output (per brand):
  01_vector_RGB/        AI + SVG + PDF (screen colour)
  02_print_CMYK/        AI + EPS + PDF/X-1a per layout: full colour, black (K100), white (knock-out), grayscale, spot
                        - converted to CMYK in Illustrator, every grey forced to a K-only value (no four-colour greys),
                          logo ink = K100, near-white = paper (0), other colours colour-managed by Illustrator
  03_screen_PNG_JPG/    transparent PNG 64-4096 (square) / 300-4800 (horizontal), JPG on white
  04_social/            avatars (IG/FB/Threads 320, X/LinkedIn/Bluesky 400, YouTube 800, LINE 640, TikTok 200, Pinterest 165,
                        generic 1080), covers (FB 851x315 + 2x, X 1500x500, LinkedIn 1584x396 / 1128x191, YouTube 2560x1440),
                        Open Graph 1200x630, e-mail signature 600 / 300 wide, YouTube watermark 150
  05_favicon_app/       favicon 16/32/48 + .ico + .svg, apple-touch 180, android 192/512, maskable 512, manifest, <head> snippet
  06_print_collateral/  business card (from the kit)
  07_guidelines/        brand guidelines PDF / PNG
  README.md             index + colour specifications
Every file is checked afterwards (sizes, CMYK-only print PDFs, spot plates) -> _package_check.json.

python tools/logo_package.py <brand config.json>   (example: examples/logo_package.example.json)
"""
import json
import re
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "lib"))
from ai_run import run_js  # noqa: E402
from ailib_loader import library  # noqa: E402
import ai_run  # noqa: E402

LIB = library()

BRANDS = {}      # loaded from a JSON config: python tools/logo_package.py <config.json> (see examples/logo_package.example.json)

SQUARE_PNG = [64, 128, 256, 512, 1024, 2048, 4096]
WIDE_PNG = [300, 600, 1200, 2400, 4800]
AVATARS = [("instagram-facebook-threads", 320), ("x-linkedin-bluesky", 400), ("youtube", 800), ("line", 640), ("tiktok", 200), ("pinterest", 165), ("generic", 1080)]
COVERS = [("facebook-cover", 851, 315), ("facebook-cover-2x", 1702, 630), ("x-header", 1500, 500), ("linkedin-personal-cover", 1584, 396),
          ("linkedin-company-cover", 1128, 191), ("youtube-banner", 2560, 1440), ("open-graph", 1200, 630)]

# ── Illustrator scripts ─────────────────────────────────────────────────────────────────────────────
JS_FILLS = r"""
while (app.documents.length) app.documents[0].close(SaveOptions.DONOTSAVECHANGES);
var D = app.open(new File(%(src)s)); try { app.executeMenuCommand('consolidateAllWindows'); } catch (e) {}
function rgb(c) { return c.typename == 'RGBColor' ? [Math.round(c.red), Math.round(c.green), Math.round(c.blue)] : null; }
var out = [];
for (var i = 0; i < D.pathItems.length; i++) { var p = D.pathItems[i], e = {i: i};
  if (p.filled) { var c = p.fillColor; if (c.typename == 'RGBColor') e.rgb = rgb(c);
    else if (c.typename == 'GradientColor') { e.grad = []; for (var s = 0; s < c.gradient.gradientStops.length; s++) e.grad.push(rgb(c.gradient.gradientStops[s].color)); } }
  out.push(e); }
J({n: out.length, fills: out, mode: String(D.documentColorSpace)})
"""
JS_TO_CMYK = "app.executeMenuCommand('doc-color-cmyk'); String(app.activeDocument.documentColorSpace)"
JS_APPLY = r"""
var O = %(opt)s, D = app.activeDocument;
function cmyk(v) { var x = new CMYKColor(); x.cyan = v[0]; x.magenta = v[1]; x.yellow = v[2]; x.black = v[3]; return x; }
var spot = null;
if (O.spot) { try { spot = D.spots.getByName(O.spot.name); } catch (e) { spot = D.spots.add(); spot.name = O.spot.name; spot.color = cmyk(O.spot.cmyk); spot.colorType = ColorModel.SPOT; } }
function spotColor(t) { var s = new SpotColor(); s.spot = spot; s.tint = t; return s; }
var done = 0, grads = {};
for (var k = 0; k < O.map.length; k++) { var m = O.map[k], p = D.pathItems[m.i];
  if (m.solid) { p.fillColor = m.solid.spot !== undefined ? spotColor(m.solid.spot) : cmyk(m.solid); done++; }
  else if (m.stops) { var g = p.fillColor.gradient;            // gradients may be shared between paths: recolour each gradient once
    if (!grads[g.name]) { for (var s = 0; s < g.gradientStops.length && s < m.stops.length; s++) g.gradientStops[s].color = cmyk(m.stops[s]); grads[g.name] = 1; }
    done++; } }
var nonK = 0, total = 0;                                   // audit: colours that are not K-only (four-colour greys would be a print fault)
var kset = {};
function audit(c) { if (c.typename == 'CMYKColor') { total++; if (c.cyan > 0.5 || c.magenta > 0.5 || c.yellow > 0.5) nonK++; else kset['K' + Math.round(c.black)] = 1; } }
for (var i = 0; i < D.pathItems.length; i++) { var p = D.pathItems[i]; if (!p.filled) continue; var c = p.fillColor;
  if (c.typename == 'GradientColor') { for (var s = 0; s < c.gradient.gradientStops.length; s++) audit(c.gradient.gradientStops[s].color); } else audit(c); }
var base = O.dir + '/' + O.stem;
var ai = new IllustratorSaveOptions(); ai.pdfCompatible = true; D.saveAs(new File(base + '.ai'), ai);
var eps = new EPSSaveOptions(); eps.cmykPostScript = true; eps.embedAllFonts = true; eps.includeDocumentThumbnails = true; eps.preview = EPSPreview.COLORTIFF;
D.saveAs(new File(base + '.eps'), eps);
var pdf = new PDFSaveOptions(); pdf.pDFXStandard = PDFXStandard.PDFX1A2001; pdf.compatibility = PDFCompatibility.ACROBAT4; pdf.preserveEditability = false;
D.saveAs(new File(base + '.pdf'), pdf);
var mode = String(D.documentColorSpace); D.close(SaveOptions.DONOTSAVECHANGES); var ks = []; for (var q in kset) ks.push(q); J({recoloured: done, mode: mode, nonK: nonK, colours: total, kValues: ks.join(' ')})
"""
JS_SCREEN = r"""
var O = %(opt)s;
while (app.documents.length) app.documents[0].close(SaveOptions.DONOTSAVECHANGES);
var D = app.open(new File(O.src)); try { app.executeMenuCommand('consolidateAllWindows'); } catch (e) {}
var a = D.artboards[0].artboardRect, W = a[2] - a[0], H = a[1] - a[3], out = [];
for (var i = 0; i < O.pngs.length; i++) { var q = O.pngs[i], s = (q[0] == 'w' ? q[1] / W : q[1] / H) * 100;
  if (s > 776) s = 776;                                          // Illustrator's PNG export limit; larger files are resampled below
  AI.png(q[2], {scale: s, transparent: true}); out.push(q[2]); }
if (O.pdf) { var p = new PDFSaveOptions(); p.preserveEditability = false; D.saveAs(new File(O.pdf), p); }
D.close(SaveOptions.DONOTSAVECHANGES); J({W: W, H: H, n: out.length})
"""
JS_COMPOSE = r"""
var O = %(opt)s;
while (app.documents.length) app.documents[0].close(SaveOptions.DONOTSAVECHANGES);
var res = [];
for (var n = 0; n < O.items.length; n++) {
  var it = O.items[n];
  var D = AI.newDoc(it.w, it.h, 'c', {units: 'px'});
  var bg = D.activeLayer.pathItems.rectangle(D.artboards[0].artboardRect[1], D.artboards[0].artboardRect[0], it.w, it.h); bg.filled = true; bg.fillColor = AI.hex(it.bg); bg.stroked = false;
  var g = D.activeLayer.groupItems.createFromFile(new File(it.svg));
  AI.scaleTo(g, it.boxW, it.boxH, true); var b = AI.box(g); AI.moveTo(g, (it.w - b.w) / 2, (it.h - b.h) / 2);
  if (it.jpg) AI.jpg(it.out, {quality: 92}); else AI.png(it.out, {transparent: false});
  D.close(SaveOptions.DONOTSAVECHANGES); res.push(it.out);
}
J(res)
"""


def js(script, opt=None, timeout=600, tries=3, dialog="esc"):
    for k in range(tries):
        try:
            return run_js(LIB + (script % opt if opt is not None else script), timeout=timeout, dialog=dialog)
        except Exception as e:  # noqa: BLE001
            if k == tries - 1 or not (ai_run.is_fault(e) or "PARM" in str(e) or not ai_run.healthy()):   # PARM on a plain DOM read = stuck engine
                raise
            print("   engine fault -> restart Illustrator and retry", flush=True)
            ai_run.restart()


def grey(v):
    return max(v) - min(v) <= 12          # neutral greys incl. the slightly cool silver (#9A9CA1)


INK_MAP = {}      # brand-specified greys: exact hex -> K value (set per brand in package())


def k_of(v):
    hx = "#%02x%02x%02x" % tuple(v)
    if hx in INK_MAP:
        return INK_MAP[hx]
    lum = sum(v) / 3
    if lum < 40:
        return 100            # logo ink
    if lum > 235:
        return 0              # near-white = paper / knock-out
    return round(100 * (1 - lum / 255))


def rule_map(fills, rule):
    """Per-path CMYK assignment from the RGB fills recorded before conversion (None entries keep Illustrator's conversion)."""
    spot = None
    if rule.startswith("spot:"):
        _, name, cm = rule.split(":")
        spot = {"name": name, "cmyk": [float(x) for x in cm.split(",")]}
    out = []
    for e in fills:
        if "rgb" in e and e["rgb"]:
            v = e["rgb"]
            if rule == "black":
                out.append({"i": e["i"], "solid": [0, 0, 0, 100]})
            elif rule == "white":
                out.append({"i": e["i"], "solid": [0, 0, 0, 0]})
            elif spot:
                out.append({"i": e["i"], "solid": {"spot": 100} if (grey(v) and sum(v) / 3 < 200) or not grey(v) else [0, 0, 0, k_of(v)]})
            elif grey(v):
                out.append({"i": e["i"], "solid": [0, 0, 0, k_of(v)]})
        elif "grad" in e and e["grad"]:
            stops = e["grad"]
            if rule in ("black", "white"):
                out.append({"i": e["i"], "solid": [0, 0, 0, 100 if rule == "black" else 0]})
            elif spot:
                out.append({"i": e["i"], "solid": {"spot": 100}})
            elif all(s and grey(s) for s in stops):
                out.append({"i": e["i"], "stops": [[0, 0, 0, k_of(s)] for s in stops]})
    return out, spot


def png_plan(B, lay):
    """(size by 'w'|'h', sizes, filename tag). Config "png_sizes": {"<layout>": {"by": "h", "sizes": [24, 40, …]}} overrides;
    otherwise the horizontal layout gets widths, square layouts get squares."""
    spec = B.get("png_sizes", {}).get(lay)
    if spec:
        return spec["by"], spec["sizes"], spec["by"]
    return ("w", WIDE_PNG, "w") if lay == "horizontal" else ("w", SQUARE_PNG, "px")


def resample(path, want_w=None, want_h=None):
    from PIL import Image
    im = Image.open(path)
    w, h = im.size
    if want_w and w != want_w:
        im.resize((want_w, round(h * want_w / w)), Image.LANCZOS).save(path)
    elif want_h and h != want_h:
        im.resize((round(w * want_h / h), want_h), Image.LANCZOS).save(path)


def package(key):
    B = BRANDS[key]
    INK_MAP.clear()
    INK_MAP.update(B.get("ink_map", {}))
    kit, out = Path(B["kit"]), Path(B["out"])
    if out.exists():                                   # clear old files (a folder handle may still be open in Explorer / Illustrator)
        for f in out.rglob("*"):
            if f.is_file():
                try:
                    f.unlink()
                except OSError:
                    pass
    dirs = {k: out / k for k in ("01_vector_RGB", "02_print_CMYK", "03_screen_PNG_JPG", "04_social", "05_favicon_app", "06_print_collateral", "07_guidelines")}
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    log = {"print": {}, "screen": {}, "social": [], "copied": []}
    slug = B["slug"]
    # 01 vector RGB: AI + SVG straight from the kit, + a vector PDF made in Illustrator below (screen pass)
    for lay, (grp, stem) in B["layouts"].items():
        for tone, sfx in B["tones"].items():
            for ext in (".ai", ".svg"):
                src = kit / grp / f"{stem}{sfx}{ext}"
                if src.exists():
                    shutil.copy2(src, dirs["01_vector_RGB"] / f"{stem}{sfx}_RGB{ext}")
    # 02 print CMYK
    for lay, (grp, stem) in B["layouts"].items():
        for pname, (tone, rule) in B["print_sets"].items():
            src = kit / grp / f"{stem}{B['tones'][tone]}.ai"
            t = time.time()
            info = json.loads(js(JS_FILLS, {"src": json.dumps(src.as_posix())}))
            js(JS_TO_CMYK)
            m, spot = rule_map(info["fills"], rule)
            r = json.loads(js(JS_APPLY, {"opt": json.dumps({"map": m, "spot": spot, "dir": dirs["02_print_CMYK"].as_posix(), "stem": f"{stem}_{pname}_CMYK" if not spot else f"{stem}_{pname}"})}, dialog="enter"))   # EPS / PDF-X warnings: accept
            log["print"][f"{stem}_{pname}"] = dict(r, paths=info["n"], mapped=len(m), rule=rule)
            print(f"print  {stem:28s} {pname:20s} {r['mode']:28s} recoloured {r['recoloured']}/{info['n']}  non-K {r['nonK']}/{r['colours']}  K used: {r.get('kValues', '')[:60]}  {time.time() - t:.0f}s", flush=True)
            if B.get("k_only") and pname in B["k_only"] and r["nonK"]:
                log.setdefault("problems", []).append(f"{stem}_{pname}: {r['nonK']} non-K colours")
    # 03 screen PNG + vector PDF (RGB)
    for lay, (grp, stem) in B["layouts"].items():
        for tone, sfx in B["tones"].items():
            src = kit / grp / f"{stem}{sfx}.ai"
            if not src.exists():
                continue
            by, sizes, tag = png_plan(B, lay)
            q = [(by, s, (dirs["03_screen_PNG_JPG"] / f"{stem}{sfx}_RGB_{s}{tag}.png").as_posix()) for s in sizes]
            r = json.loads(js(JS_SCREEN, {"opt": json.dumps({"src": src.as_posix(), "pngs": q, "pdf": (dirs["01_vector_RGB"] / f"{stem}{sfx}_RGB.pdf").as_posix()})}))
            for b, s, fn in q:
                resample(fn, want_w=s) if b == "w" else resample(fn, want_h=s)
            log["screen"][f"{stem}{sfx}"] = r
            print(f"screen {stem}{sfx}: {len(q)} png + pdf", flush=True)
    # 03 JPG on white / on brand dark (square logo)
    grp, stem = B["layouts"]["logo"]
    items = []
    for bgname, bg, tone in (("white", B["bg_light"], "color"), ("dark", B["bg_dark"], "dark")):
        svg = (kit / grp / f"{stem}{B['tones'][tone]}.svg").as_posix()
        for s in (1080, 2048):
            items.append(dict(w=s, h=s, bg=bg, svg=svg, boxW=s * 0.72, boxH=s * 0.72, jpg=True, out=(dirs["03_screen_PNG_JPG"] / f"{stem}_on-{bgname}_RGB_{s}px.jpg").as_posix()))
    # 04 social
    avatar_svg = (kit / B["layouts"]["mark"][0] / f"{B['layouts']['mark'][1]}{B['tones'][B['avatar_tone']]}.svg").as_posix()
    logo_dark_svg = (kit / grp / f"{stem}{B['tones']['dark']}.svg").as_posix()
    hgrp, hstem = B["layouts"]["horizontal"]
    h_dark_svg = (kit / hgrp / f"{hstem}{B['tones']['dark']}.svg").as_posix()
    h_light_svg = (kit / hgrp / f"{hstem}.svg").as_posix()
    for name, s in AVATARS:     # circle-safe: the mark inside 62 % of the side (avatars are cropped to a circle)
        items.append(dict(w=s, h=s, bg=B["avatar_bg"], svg=avatar_svg, boxW=s * 0.62, boxH=s * 0.62, out=(dirs["04_social"] / f"{slug}_avatar_{name}_{s}x{s}.png").as_posix()))
        if name == "generic":
            items.append(dict(w=s, h=s, bg=B["bg_dark"], svg=logo_dark_svg, boxW=s * 0.66, boxH=s * 0.66, out=(dirs["04_social"] / f"{slug}_avatar_logo_{s}x{s}.png").as_posix()))
    for name, w, h in COVERS:
        if name == "youtube-banner":            # logo inside the 1546 x 423 area safe on every device
            bw, bh = 1546 * 0.8, 423 * 0.8
        elif name == "linkedin-company-cover":
            bw, bh = w * 0.5, h * 0.5
        else:
            bw, bh = w * 0.56, h * 0.42
        items.append(dict(w=w, h=h, bg=B["bg_dark"], svg=h_dark_svg, boxW=bw, boxH=bh, out=(dirs["04_social"] / f"{slug}_{name}_{w}x{h}.png").as_posix()))
    items.append(dict(w=150, h=150, bg=B["bg_dark"], svg=avatar_svg if B["avatar_bg"] == B["bg_dark"] else (kit / B["layouts"]["mark"][0] / f"{B['layouts']['mark'][1]}{B['tones']['dark']}.svg").as_posix(),
                      boxW=120, boxH=120, out=(dirs["04_social"] / f"{slug}_youtube-watermark_150x150.png").as_posix()))
    for w in (600, 300):
        items.append(dict(w=w, h=round(w * 0.3), bg=B["bg_light"], svg=h_light_svg, boxW=w * 0.94, boxH=w * 0.3 * 0.86, out=(dirs["04_social"] / f"{slug}_email-signature_{w}w.png").as_posix()))
    for k in range(0, len(items), 8):
        js(JS_COMPOSE, {"opt": json.dumps({"items": items[k:k + 8]})}, timeout=900)
    log["social"] = [i["out"] for i in items]
    print(f"composed {len(items)} social / jpg files", flush=True)
    # 05 favicon / app
    for p in (kit / B["favicon"]).glob("*"):
        if p.suffix in (".png", ".ico", ".svg"):
            shutil.copy2(p, dirs["05_favicon_app"] / p.name)
    for p in (kit / B["icon"]).glob("*.png"):
        shutil.copy2(p, dirs["05_favicon_app"] / p.name)
    for p in (kit / "web").glob("*"):
        shutil.copy2(p, dirs["05_favicon_app"] / p.name)
    from PIL import Image
    ic = sorted((kit / B["icon"]).glob("*512w.png"))
    if ic:                                        # maskable: content inside the central 80 % circle
        im = Image.open(ic[0]).convert("RGBA")
        bgc = im.getpixel((2, 2))
        canvas = Image.new("RGBA", (512, 512), bgc)
        inner = im.resize((410, 410), Image.LANCZOS)
        canvas.paste(inner, (51, 51), inner)
        canvas.save(dirs["05_favicon_app"] / f"{slug}_maskable_512x512.png")
    # 06 collateral, 07 guidelines
    for p in (kit / B["card"]).glob("*"):
        shutil.copy2(p, dirs["06_print_collateral"] / p.name)
    for g in B["guide"]:
        if (kit / g).exists():
            shutil.copy2(kit / g, dirs["07_guidelines"] / g)
    (out / "_package_log.json").write_text(json.dumps(log, indent=1, ensure_ascii=False), encoding="utf-8")
    return out


def check(key):
    """Verify the package: PNG sizes, print PDFs CMYK-only (+ spot plate), PDF/X, every print set has AI/EPS/PDF."""
    import pypdf
    from PIL import Image
    B = BRANDS[key]
    out = Path(B["out"])
    rep = {"png_size": [], "print": {}, "problems": []}
    for p in (out / "03_screen_PNG_JPG").glob("*.png"):
        m = re.search(r"_(\d+)(px|w|h)\.png$", p.name)
        w, h = Image.open(p).size
        n = int(m.group(1)) if m else 0
        ok = m and ((m.group(2) == "w" and w == n) or (m.group(2) == "h" and h == n) or (m.group(2) == "px" and w == h == n))
        rep["png_size"].append([p.name, w, h, bool(ok)])
        if not ok:
            rep["problems"].append(f"size {p.name} {w}x{h}")
    for p in (out / "04_social").glob("*.png"):
        m = re.search(r"_(\d+)x(\d+)\.png$", p.name) or re.search(r"_(\d+)w\.png$", p.name)
        w, h = Image.open(p).size
        if m and len(m.groups()) == 2 and (w, h) != (int(m.group(1)), int(m.group(2))):
            rep["problems"].append(f"size {p.name} {w}x{h}")
        if m and len(m.groups()) == 1 and w != int(m.group(1)):
            rep["problems"].append(f"size {p.name} {w}x{h}")
    for lay, (grp, stem) in B["layouts"].items():
        for pname, (tone, rule) in B["print_sets"].items():
            base = out / "02_print_CMYK" / (f"{stem}_{pname}" if rule.startswith("spot:") else f"{stem}_{pname}_CMYK")
            files = {e: (base.with_suffix(e)).exists() for e in (".ai", ".eps", ".pdf")}
            info = {"files": files}
            if files[".pdf"]:
                r = pypdf.PdfReader(str(base.with_suffix(".pdf")))
                rgb_ops, seps = 0, set()
                for pg in r.pages:
                    data = pg.get_contents().get_data() if pg.get_contents() else b""
                    rgb_ops += len(re.findall(rb"(?<![\w.])(rg|RG)(?![\w])", data))
                    res = pg["/Resources"]
                    for v in (res.get("/ColorSpace") or {}).values():
                        o = v.get_object()
                        if isinstance(o, list):
                            seps.add(str(o[0]) + ":" + str(o[1]))
                            if "DeviceRGB" in str(o[2:3]) or str(o[0]) == "/ICCBased":
                                pass
                    for sh in ((res.get("/Shading") or {}).values()):
                        cs = str(sh.get_object().get("/ColorSpace"))
                        if "RGB" in cs:
                            rgb_ops += 1
                info.update(rgb_ops=rgb_ops, separations=sorted(seps), pdfx=str(r.metadata.get("/GTS_PDFXConformance") if r.metadata else None))
                if rgb_ops:
                    rep["problems"].append(f"RGB in {base.name}.pdf ({rgb_ops})")
                if rule.startswith("spot:") and not any(rule.split(":")[1] in s for s in seps):
                    rep["problems"].append(f"spot plate missing in {base.name}.pdf")
            if not all(files.values()):
                rep["problems"].append(f"missing {base.name} {files}")
            rep["print"][base.name] = info
    lg = json.loads((out / "_package_log.json").read_text(encoding="utf-8"))
    rep["problems"] += lg.get("problems", [])
    rep["print_colour_audit"] = {k: {"nonK": v.get("nonK"), "colours": v.get("colours")} for k, v in lg["print"].items()}
    (out / "_package_check.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False), encoding="utf-8")
    return rep


def readme(key):
    B = BRANDS[key]
    out = Path(B["out"])
    n = {d.name: len([p for p in d.iterdir() if p.is_file()]) for d in sorted(out.iterdir()) if d.is_dir()}
    lines = [f"# {B['name']} logo package", "",
             "Produced in Adobe Illustrator from the vector masters; every file checked by `tools/logo_package.py` (see `_package_check.json`).", "",
             "| Folder | Files | Use |", "|---|---|---|",
             f"| 01_vector_RGB | {n.get('01_vector_RGB', 0)} | AI / SVG / PDF in RGB: web, apps, presentations, video. SVG is the file for websites. |",
             f"| 02_print_CMYK | {n.get('02_print_CMYK', 0)} | AI / EPS / PDF (PDF/X-1a) in CMYK for print: full colour, black K100, white (knock-out), grayscale, spot colour. Greys are K-only; logo ink K100. Send the PDF or EPS to the printer. |",
             f"| 03_screen_PNG_JPG | {n.get('03_screen_PNG_JPG', 0)} | Transparent PNG (64–4096 px square, 300–4800 px wide) and JPG on white / dark. Never use these for print. |",
             f"| 04_social | {n.get('04_social', 0)} | Avatars (IG/FB/Threads 320, X/LinkedIn/Bluesky 400, YouTube 800, LINE 640, TikTok 200, Pinterest 165, 1080), covers (FB, X, LinkedIn, YouTube 2560×1440 with the logo inside the 1546×423 safe area), Open Graph 1200×630, e-mail signature 600/300, YouTube watermark 150. |",
             f"| 05_favicon_app | {n.get('05_favicon_app', 0)} | favicon 16/32/48 + .ico + .svg, apple-touch-icon 180, Android 192/512, maskable 512, site.webmanifest, head-snippet.html. |",
             f"| 06_print_collateral | {n.get('06_print_collateral', 0)} | Business card: .ai + PDF/X-1a (90×54 mm, 3 mm bleed, trim marks, foil spot plate) + previews. |",
             f"| 07_guidelines | {n.get('07_guidelines', 0)} | Brand guidelines (PDF / PNG). |", "",
             "## Colour specifications", "", "| Colour | Screen (RGB / HEX) | Print (CMYK) | Spot |", "|---|---|---|---|"]
    lines += [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in B["colors"]]
    lines += ["", "Spot colours are named for the printer (metallic Pantone references with a CMYK fallback defined in the file); confirm the exact ink / foil against the printer's physical swatch book before production.",
              "", "## File naming", "", "`<brand>-<layout>[-tone]_<variant>_<colour space>.<ext>` — layout: logo (square, primary) · logo-horizontal (secondary) · mark (symbol).", ""]
    (out / "README.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    cfg = Path(sys.argv[1])
    key = cfg.stem
    BRANDS[key] = json.loads(cfg.read_text(encoding="utf-8"))
    for k, v in BRANDS[key].get("layouts", {}).items():
        BRANDS[key]["layouts"][k] = tuple(v)
    for k, v in BRANDS[key].get("print_sets", {}).items():
        BRANDS[key]["print_sets"][k] = tuple(v)
    t = time.time()
    package(key)
    rep = check(key)
    readme(key)
    print(f"{key}: problems {len(rep['problems'])} -> {rep['problems'][:10]}  ({time.time() - t:.0f}s)")

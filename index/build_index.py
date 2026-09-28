"""Build the Illustrator ExtendScript API index from YOUR Illustrator (no third-party index needed).

Source 1: the type library. Illustrator ships "Adobe Illustrator NN Type Library" inside
          Plug-ins/Extensions/ScriptingSupport.aip; pythoncom.LoadTypeLib reads it even when COM is unregistered:
          classes, properties (type, read-only), methods (arguments), enums (values) and Adobe's help strings.
Source 2: runtime check. In a sandbox document a real instance of every class is created and its ExtendScript
          `reflect` member list is read; every enum member is probed. The COM name is matched to the real
          ExtendScript spelling (ActiveDocument -> activeDocument, aiColorBurn -> BlendModes.COLORBURN).
Output: index/ai-dom.json (queried by index/ai_api.py)
Usage:  python index/build_index.py [--ai "C:/Program Files/Adobe/Adobe Illustrator 2024"]
"""
import argparse
import json
import re
import sys
from pathlib import Path

import pythoncom

HERE = Path(__file__).parent
LIB = HERE.parent / "lib"
sys.path.insert(0, str(LIB))
from ai_run import run_js  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--ai", default=r"C:\Program Files\Adobe\Adobe Illustrator 2024")
a = ap.parse_args()
TLB = Path(a.ai) / "Plug-ins" / "Extensions" / "ScriptingSupport.aip"

VT = {2: "short", 3: "long", 4: "float", 5: "double", 8: "string", 9: "object", 11: "boolean", 12: "any",
      13: "object", 16: "char", 17: "byte", 18: "ushort", 19: "ulong", 22: "int", 23: "uint", 24: "void",
      25: "HRESULT", 7: "date", 6: "currency"}
SKIP = {"QueryInterface", "AddRef", "Release", "GetTypeInfoCount", "GetTypeInfo", "GetIDsOfNames", "Invoke"}


def clean(n):
    n = n.lstrip("_")
    return n[2:] if n.startswith("Ai") and n[2:3].isupper() else n


def tname(ti, td):
    if isinstance(td, tuple) and len(td) == 3:          # ELEMDESC (typedesc, flags, default)
        td = td[0]
    if isinstance(td, tuple):
        vt, inner = td
        if vt == 26:
            return tname(ti, inner)
        if vt == 27:
            return "array of " + tname(ti, inner)
        if vt == 29:
            return clean(ti.GetRefTypeInfo(inner).GetDocumentation(-1)[0])
        return VT.get(vt, f"vt{vt}")
    return VT.get(td, f"vt{td}")


def words(s):
    return re.findall(r"[A-Z]+(?=[A-Z][a-z]|\d|\b)|[A-Z]?[a-z]+|\d+|[A-Z]+", s)


NUMW = {"1": "ONE", "2": "TWO", "3": "THREE", "4": "FOUR", "8": "EIGHT", "16": "SIXTEEN", "24": "TWENTYFOUR", "32": "THIRTYTWO"}


def enum_candidates(member):
    """aiColorBurn -> COLORBURN; aiDocumentRGBColor -> RGB; aiNoAntialias -> NONE ... every contiguous word run
    is a candidate (longest first), numbers also spelled out; Illustrator picks the one that exists."""
    base = member[2:] if member.startswith("ai") else member
    w = words(base[0].upper() + base[1:])
    c = []
    for L in range(len(w), 0, -1):
        for i in range(0, len(w) - L + 1):
            seg = w[i:i + L]
            c.append("".join(seg).upper())
            c.append("_".join(seg).upper())
            if any(x in NUMW for x in seg):
                c.append("".join(NUMW.get(x, x) for x in seg).upper())
    if w and w[0] == "No":
        c.insert(0, "NONE")
    for L in range(len(w), 0, -1):                      # some enums use camelCase members (StyleRunAlignmentType.bottom)
        for i in range(0, len(w) - L + 1):
            seg = w[i:i + L]
            c.append(seg[0].lower() + "".join(seg[1:]))
            c.append(seg[0] + "".join(seg[1:]))
    raw = member[2:] if member.startswith("ai") else member
    c += [raw, raw.upper()]
    alias = {"UnitsCM": "Centimeters", "UnitsMM": "Millimeters", "UnitsQ": "Qs"}
    if raw in alias:
        c.insert(0, alias[raw])
    return list(dict.fromkeys(c))


def enum_js_candidates(com):
    n = clean(com)
    extra = {"ExportFileType": "ExportType", "Color": "ColorType"}
    return list(dict.fromkeys(([extra[n]] if n in extra else []) + [n, re.sub(r"Type$", "", n), re.sub(r"s$", "", n), n + "s", re.sub(r"Type$", "", n) + "s", re.sub(r"Values$", "", n)]))


# ── 1. type library ─────────────────────────────────────────────────────────
tl = pythoncom.LoadTypeLib(str(TLB))
classes, enums = {}, {}
for i in range(tl.GetTypeInfoCount()):
    ti = tl.GetTypeInfo(i)
    at = ti.GetTypeAttr()
    name, doc = ti.GetDocumentation(-1)[:2]
    if at.typekind == pythoncom.TKIND_ENUM:
        mem = {}
        for j in range(at.cVars):
            vd = ti.GetVarDesc(j)
            n, h = ti.GetDocumentation(vd.memid)[:2]
            mem[n] = {"value": vd.value, "help": h or ""}
        enums[name] = {"help": doc or "", "members": mem}
    elif at.typekind in (pythoncom.TKIND_DISPATCH, pythoncom.TKIND_INTERFACE):
        cn = clean(name)
        c = classes.setdefault(cn, {"com": name, "help": doc or "", "props": {}, "methods": {}})
        for j in range(at.cFuncs):
            fd = ti.GetFuncDesc(j)
            names = ti.GetNames(fd.memid)
            n = names[0]
            if n in SKIP:
                continue
            h = ti.GetDocumentation(fd.memid)[1] or ""
            if fd.invkind == pythoncom.INVOKE_FUNC:
                args = []
                for k, ad in enumerate(fd.args):
                    args.append({"name": names[k + 1] if k + 1 < len(names) else f"arg{k}", "type": tname(ti, ad[0]),
                                 "optional": bool(ad[1] & 16) or k >= len(fd.args) - fd.cParamsOpt})
                c["methods"][n] = {"args": args, "returns": tname(ti, fd.rettype), "help": h}
            else:
                p = c["props"].setdefault(n, {"type": None, "readonly": True, "help": h})
                if fd.invkind == pythoncom.INVOKE_PROPERTYGET:
                    p["type"] = tname(ti, fd.rettype)
                else:
                    p["readonly"] = False
                    if p["type"] is None and fd.args:
                        p["type"] = tname(ti, fd.args[-1][0])
                p["help"] = p["help"] or h
    elif at.typekind == pythoncom.TKIND_COCLASS:
        classes.setdefault(clean(name), {"com": name, "help": doc or "", "props": {}, "methods": {}})["coclass"] = True

# ── 2. runtime: instances in a sandbox document ─────────────────────────────
MAKE = r"""
var T = Folder.temp + '/ai_index_tmp'; new Folder(T).create();
var D = app.documents.add(DocumentColorSpace.RGB, 800, 800);
var R = D.pathItems.rectangle(700, 100, 200, 150); var R2 = D.pathItems.ellipse(400, 400, 120, 120);
var png = new File(T + '/probe.png'); var o = new ExportOptionsPNG24(); o.artBoardClipping = true; D.exportFile(png, ExportType.PNG24, o);
var TF = D.textFrames.pointText([100, 100]); TF.contents = 'Probe text';
var PT = D.textFrames.pathText(R2); PT.contents = 'on path';
var I = {};
function mk(n, f) { try { var v = f(); if (v !== undefined && v !== null) I[n] = v; } catch (e) { I['!' + n] = String(e); } }
mk('Application', function () { return app; }); mk('Document', function () { return D; }); mk('Documents', function () { return app.documents; });
mk('Layer', function () { return D.layers[0]; }); mk('Layers', function () { return D.layers; });
mk('PathItem', function () { return R; }); mk('PathItems', function () { return D.pathItems; });
mk('PathPoint', function () { return R.pathPoints[0]; }); mk('PathPoints', function () { return R.pathPoints; });
mk('CompoundPathItem', function () { var c = D.compoundPathItems.add(); D.pathItems.rectangle(50, 50, 20, 20).move(c, ElementPlacement.PLACEATEND); return c; });
mk('CompoundPathItems', function () { return D.compoundPathItems; });
mk('Tag', function () { var t = R.tags.add(); t.name = 'probe'; t.value = '1'; return t; }); mk('Tags', function () { return R.tags; });
mk('GroupItem', function () { var g = D.groupItems.add(); D.pathItems.rectangle(80, 80, 10, 10).move(g, ElementPlacement.PLACEATEND); return g; }); mk('GroupItems', function () { return D.groupItems; });
mk('PageItems', function () { return D.pageItems; });
mk('Matrix', function () { return app.getIdentityMatrix(); });
mk('PlacedItem', function () { var p = D.placedItems.add(); p.file = png; return p; }); mk('PlacedItems', function () { return D.placedItems; });
mk('RasterItem', function () { return D.rasterize(D.pathItems.rectangle(300, 600, 50, 50)); }); mk('RasterItems', function () { return D.rasterItems; });
mk('PluginItem', function () { var p = D.placedItems.add(); p.file = png; return p.trace(); }); mk('PluginItems', function () { return D.pluginItems; });
mk('TracingObject', function () { return I.PluginItem.tracing; }); mk('TracingOptions', function () { return I.PluginItem.tracing.tracingOptions; });
mk('Symbol', function () { return D.symbols.add(D.pathItems.star(200, 200, 30, 15, 5)); }); mk('Symbols', function () { return D.symbols; });
mk('SymbolItem', function () { return D.symbolItems.add(I.Symbol); }); mk('SymbolItems', function () { return D.symbolItems; });
mk('TextFrame', function () { return TF; }); mk('TextFrames', function () { return D.textFrames; }); mk('TextPath', function () { return PT.textPath; });
mk('Story', function () { return TF.story; }); mk('Stories', function () { return D.stories; });
mk('TextRange', function () { return TF.textRange; }); mk('TextRanges', function () { return TF.textRanges; });
mk('Characters', function () { return TF.characters; }); mk('Words', function () { return TF.words; }); mk('Lines', function () { return TF.lines; });
mk('Paragraphs', function () { return TF.paragraphs; }); mk('InsertionPoints', function () { return TF.insertionPoints; }); mk('InsertionPoint', function () { return TF.insertionPoints[0]; });
mk('CharacterStyle', function () { return D.characterStyles[0]; }); mk('CharacterStyles', function () { return D.characterStyles; });
mk('CharacterAttributes', function () { return TF.textRange.characterAttributes; });
mk('ParagraphStyle', function () { return D.paragraphStyles[0]; }); mk('ParagraphStyles', function () { return D.paragraphStyles; });
mk('ParagraphAttributes', function () { return TF.textRange.paragraphAttributes; });
mk('ListStyle', function () { return D.listStyles[0]; }); mk('ListStyles', function () { return D.listStyles; });
mk('TextFont', function () { return app.textFonts[0]; }); mk('TextFonts', function () { return app.textFonts; });
mk('View', function () { return D.views[0]; }); mk('Views', function () { return D.views; });
mk('Variable', function () { return D.variables.add(); }); mk('Variables', function () { return D.variables; });
mk('DataSet', function () { var v = D.variables.add(); v.kind = VariableKind.VISIBILITY; R.visibilityVariable = v; return D.dataSets.add(); }); mk('DataSets', function () { return D.dataSets; });
mk('RasterEffectOptions', function () { return D.rasterEffectSettings; });
mk('Artboard', function () { return D.artboards[0]; }); mk('Artboards', function () { return D.artboards; });
mk('Asset', function () { return D.assets.add(R); }); mk('Assets', function () { return D.assets; });
mk('Swatch', function () { return D.swatches[0]; }); mk('Swatches', function () { return D.swatches; });
mk('SwatchGroup', function () { return D.swatchGroups[0]; }); mk('SwatchGroups', function () { return D.swatchGroups; });
mk('Spot', function () { var s = D.spots.add(); s.name = 'probe spot'; var c = new CMYKColor(); c.cyan = 50; s.color = c; return s; }); mk('Spots', function () { return D.spots; });
mk('Gradient', function () { return D.gradients.add(); }); mk('Gradients', function () { return D.gradients; });
mk('GradientStop', function () { return I.Gradient.gradientStops[0]; }); mk('GradientStops', function () { return I.Gradient.gradientStops; });
mk('Pattern', function () { return D.patterns[0]; }); mk('Patterns', function () { return D.patterns; });
mk('Brush', function () { return D.brushes[0]; }); mk('Brushes', function () { return D.brushes; });
mk('GraphicStyle', function () { return D.graphicStyles[0]; }); mk('GraphicStyles', function () { return D.graphicStyles; });
mk('Preferences', function () { return app.preferences; });
mk('PhotoshopFileOptions', function () { return app.preferences.photoshopFileOptions; });
mk('PDFFileOptions', function () { return app.preferences.PDFFileOptions; });
mk('AutoCADFileOptions', function () { return app.preferences.AutoCADFileOptions; });
mk('EmbeddedItems', function () { return D.embeddedItems; });
mk('EmbedItem', function () { return D.embeddedItems.length ? D.embeddedItems[0] : undefined; });
mk('MeshItems', function () { return D.meshItems; }); mk('GraphItems', function () { return D.graphItems; });
mk('NonNativeItems', function () { return D.nonNativeItems; }); mk('LegacyTextItems', function () { return D.legacyTextItems; });
mk('RadialRepeatItems', function () { return D.radialRepeatItems; }); mk('GridRepeatItems', function () { return D.gridRepeatItems; }); mk('SymmetryRepeatItems', function () { return D.symmetryRepeatItems; });
mk('RadialRepeatItem', function () { D.selection = null; var e = D.pathItems.ellipse(600, 600, 30, 30); e.selected = true; app.executeMenuCommand('Make Radial Repeat'); return D.radialRepeatItems.length ? D.radialRepeatItems[0] : undefined; });
mk('RadialRepeatConfig', function () { return I.RadialRepeatItem.radialConfig; });
mk('GridRepeatItem', function () { D.selection = null; var e = D.pathItems.ellipse(150, 600, 20, 20); e.selected = true; app.executeMenuCommand('Make Grid Repeat'); return D.gridRepeatItems.length ? D.gridRepeatItems[0] : undefined; });
mk('GridRepeatConfig', function () { return I.GridRepeatItem.gridConfig; });
mk('SymmetryRepeatItem', function () { D.selection = null; var e = D.pathItems.ellipse(300, 60, 20, 20); e.selected = true; app.executeMenuCommand('Make Symmetry Repeat'); return D.symmetryRepeatItems.length ? D.symmetryRepeatItems[0] : undefined; });
mk('SymmetryRepeatConfig', function () { return I.SymmetryRepeatItem.symmetryConfig; });
mk('MeshItem', function () { D.selection = null; var e = D.pathItems.rectangle(760, 700, 40, 40); var mc = new RGBColor(); mc.red = 200; e.fillColor = mc; e.selected = true; app.executeMenuCommand('make mesh'); return D.meshItems.length ? D.meshItems[0] : undefined; });
mk('GraphItem', function () { return D.graphItems.length ? D.graphItems[0] : undefined; });
mk('DocumentPreset', function () { return new DocumentPreset(); });
mk('PrintOptions', function () { return new PrintOptions(); });
"""
COCLASS_NEW = ["OpenOptions", "FXGSaveOptions", "EPSSaveOptions", "PDFSaveOptions", "IllustratorSaveOptions",
               "ExportForScreensItemToExport", "ExportForScreensOptionsJPEG", "ExportForScreensOptionsPNG8", "ExportForScreensOptionsPNG24",
               "ExportForScreensOptionsWebOptimizedSVG", "ExportForScreensPDFOptions", "ExportForScreensOptionsWebP", "ExportOptionsJPEG",
               "ExportOptionsPNG8", "ExportOptionsPNG24", "ExportOptionsWebP", "ExportOptionsGIF", "ExportOptionsPhotoshop", "ExportOptionsSVG",
               "ExportOptionsWebOptimizedSVG", "ExportOptionsAutoCAD", "ExportOptionsTIFF", "LabColor", "Dimensions", "RGBColor", "CMYKColor", "GrayColor",
               "NoColor", "SpotColor", "PatternColor", "GradientColor", "TabStopInfo", "Printer", "PrinterInfo", "PPDFile", "PPDFileInfo", "Paper", "PaperInfo",
               "Screen", "ScreenInfo", "ScreenSpotFunction", "Ink", "InkInfo", "PrintPaperOptions", "PrintJobOptions", "PrintColorSeparationOptions",
               "PrintCoordinateOptions", "PrintPageMarksOptions", "PrintFontOptions", "PrintPostScriptOptions", "PrintColorManagementOptions",
               "PrintFlattenerOptions", "ImageCaptureOptions", "RasterizeOptions", "Matrix"]
MAKE += "".join(f"mk('{c}', function () {{ return I['{c}'] || new {c}(); }});\n" for c in COCLASS_NEW)
MAKE += r"""
var OUT = {};
for (var k in I) {
  if (k.charAt(0) == '!') { OUT[k] = I[k]; continue; }
  var o = I[k], p = [], m = [];
  try { var L = o.reflect.properties; for (var i = 0; i < L.length; i++) p.push(L[i].name); } catch (e) { p.push('!' + e); }
  try { var M = o.reflect.methods; for (var i = 0; i < M.length; i++) m.push(M[i].name); } catch (e) { m.push('!' + e); }
  OUT[k] = {p: p, m: m, t: (function () { try { return o.typename; } catch (e) { return ''; } })()};
}
D.close(SaveOptions.DONOTSAVECHANGES);
J(OUT);
"""
js = (LIB / "json.jsx").read_text(encoding="utf-8") + MAKE
rt = json.loads(run_js(js, dialog="enter"))

# second pass: members that reflect did not list (collections hide their methods) -> probe typeof on the same instances
miss = {}
for cn, c in classes.items():
    r = rt.get(cn)
    if not r:
        continue
    low = {x.lower() for x in r["p"] + r["m"]}
    cand = [n[0].lower() + n[1:] for n in c["methods"] if n.lower() not in low]   # methods only: touching getters can fault
    if cand:
        miss[cn] = cand
probe2 = (LIB / "json.jsx").read_text(encoding="utf-8") + MAKE.split("var OUT = {};")[0] + "var MISS = " + json.dumps(miss) + r""";
var OUT = {};
for (var k in MISS) { var o = I[k], hit = []; if (!o) continue;
  for (var i = 0; i < MISS[k].length; i++) { var n = MISS[k][i]; try { if (typeof o[n] != 'undefined') hit.push(n); } catch (e) { hit.push(n); } }
  OUT[k] = hit; }
D.close(SaveOptions.DONOTSAVECHANGES);
J(OUT);
"""
extra_hits = json.loads(run_js(probe2, dialog="enter"))
for cn, hits in extra_hits.items():
    rt[cn]["m"] += hits

# enum probing
ecand = {}
for en, e in enums.items():
    ecand[en] = {"js": enum_js_candidates(en), "m": {m: enum_candidates(m) for m in e["members"]}}
probe = (LIB / "json.jsx").read_text(encoding="utf-8") + "var C = " + json.dumps(ecand) + r""";
function has(o, k) { try { var v = o[k]; return v !== undefined && v !== null; } catch (e) { return false; } }
var R = {};
for (var en in C) {
  var js = null;
  for (var i = 0; i < C[en].js.length; i++) { try { if (eval('typeof ' + C[en].js[i]) != 'undefined') { js = C[en].js[i]; break; } } catch (e) {} }
  var mm = {};
  if (js) { var E = eval(js); for (var m in C[en].m) { var L = C[en].m[m]; mm[m] = null; for (var j = 0; j < L.length; j++) if (has(E, L[j])) { mm[m] = L[j]; break; } } }
  R[en] = {js: js, m: mm};
}
J(R);
"""
er = json.loads(run_js(probe))

# ── 3. merge ────────────────────────────────────────────────────────────────
# COM plumbing that ExtendScript spells differently (or does not have): name -> ExtendScript equivalent
COM_ONLY = {"Application": "app", "ObjectValue": None, "Count": "collection.length", "_NewEnum": "for (i < length)",
            "Item": "collection[i] / collection.getByName(name)", "Index": "collection[i]", "Delete": "remove()",
            "Cut": "app.executeMenuCommand('cut')", "Copy": "app.executeMenuCommand('copy')", "Paste": "app.executeMenuCommand('paste')",
            "MoveToBeginning": "move(target, ElementPlacement.PLACEATBEGINNING)", "MoveToEnd": "move(target, ElementPlacement.PLACEATEND)",
            "MoveBefore": "move(target, ElementPlacement.PLACEBEFORE)", "MoveAfter": "move(target, ElementPlacement.PLACEAFTER)",
            "PageItem": "the item itself (typename)", "PageItemType": "item.typename", "CompoundPathItem": "typename check", "GraphItem": "typename check",
            "GroupItem": "typename check", "MeshItem": "typename check", "PathItem": "typename check", "PlacedItem": "typename check",
            "PluginItem": "typename check", "RasterItem": "typename check", "SymbolItem": "typename check", "TextFrame": "typename check",
            "LegacyTextItem": "typename check", "NonNativeItem": "typename check", "EmbeddedItem": "typename check",
            "Export": "exportFile()", "PrintOut": "print()", "ImportFileIntoDocument": "importFile()", "DoJavaScript": "(COM entry point)",
            "DoJavaScriptFile": "$.evalFile()", "ExportSelectedArtwork": "exportSelectionAsAi()", "Parent": "parent", "RemoveAll": "removeAll()"}
n_ver = n_all = 0
for cn, c in classes.items():
    r = rt.get(cn)
    c["runtime"] = r["t"] if r else None
    c["js"] = cn
    lowp = {x.lower(): x for x in (r["p"] if r else [])}
    lowm = {x.lower(): x for x in (r["m"] if r else [])}
    for group, low in (("props", lowp), ("methods", lowm)):
        for n, x in c[group].items():
            n_all += 1
            hit = low.get(n.lower()) or (lowp if group == "methods" else lowm).get(n.lower())
            x["js"] = hit or (n[0].lower() + n[1:] if not n[:2].isupper() else n)
            x["verified"] = bool(hit)
            if not hit and n in COM_ONLY:
                x["com_only"] = True
                x["js_equiv"] = COM_ONLY[n]
            n_ver += bool(hit)
    # members that exist in ExtendScript but not in the type library (JS-only)
    if r:
        known = {n.lower() for n in c["props"]} | {n.lower() for n in c["methods"]}
        c["js_only"] = sorted(x for x in r["p"] + r["m"] if x.lower() not in known and not x.startswith("!") and x not in ("reflect", "toString", "valueOf", "hasOwnProperty", "toSource", "isPrototypeOf", "propertyIsEnumerable", "watch", "unwatch", "constructor", "__proto__", "__count__", "__class__"))
for en, e in enums.items():
    r = er.get(en, {})
    e["js"] = r.get("js")
    for m, x in e["members"].items():
        v = (r.get("m") or {}).get(m)
        x["js"] = f"{r['js']}.{v}" if v and r.get("js") else None
        x["verified"] = bool(v)

data = {"version": run_js("app.version"), "source": str(TLB), "classes": classes, "enums": enums,
        "runtime_errors": {k: v for k, v in rt.items() if k.startswith("!")}}
(HERE / "ai-dom.json").write_text(json.dumps(data, ensure_ascii=False, indent=0), encoding="utf-8")
em = sum(len(e["members"]) for e in enums.values())
ev = sum(x["verified"] for e in enums.values() for x in e["members"].values())
n_com = sum(1 for c in classes.values() for g in ("props", "methods") for x in c[g].values() if x.get("com_only"))
print(f"Illustrator {data['version']}: {len(classes)} classes ({sum(1 for c in classes.values() if c['runtime'])} instantiated), "
      f"{n_all} members ({n_ver} verified in ExtendScript, {n_com} COM-only), {len(enums)} enums with {em} members ({ev} verified)")
print("could not instantiate:", sorted(k for k, c in classes.items() if not c["runtime"]))
print("errors:", data["runtime_errors"])

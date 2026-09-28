"""Tools sweep: every tool in index/menu-index.json (from the app's own shortcut set).
1. app.selectTool(name) and read back app.getSelectedToolName()  -> the tool can be activated from a script
2. the drawing a tool does by hand -> the scripted equivalent (ailib function / DOM call), each covered by a test in
   tests/REPORT.md or the menu sweep. Tools that only exist as mouse gestures are listed as such.
Output: tests/tools-sweep.json, section in tests/CAPABILITIES.md (build_coverage.py)
Usage:  python tests/tools_sweep.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
SKILL = HERE.parent
sys.path.insert(0, str(SKILL / "lib"))
sys.stdout.reconfigure(encoding="utf-8")
from ai_run import run_js  # noqa: E402

EQUIV = {
    "Adobe Select Tool": "document.selection = items / AI.select()", "Adobe Direct Select Tool": "pathPoint.selected = PathPointSelection.ANCHORPOINT",
    "Adobe Direct Object Select Tool": "select an item inside a group: group.pageItems[i].selected = true", "Adobe Magic Wand Tool": "Select > Same > … (menu sweep)",
    "Adobe Direct Lasso Tool": "pathPoint.selected by region (loop points inside a polygon)", "Adobe Pen Tool": "AI.path(points) / pathItem.setEntirePath() + pathPoints[i].leftDirection/rightDirection",
    "Adobe Curvature Tool": "AI.path([[x, y, inX, inY, outX, outY], …]) smooth points", "Adobe Add Anchor Point Tool": "Object > Path > Add Anchor Points / pathPoints.add()",
    "Adobe Delete Anchor Point Tool": "pathPoint.remove()", "Adobe Anchor Point Tool": "pathPoint.pointType = PointType.SMOOTH / CORNER",
    "Adobe Type Tool": "AI.text(str, x, y, {…}) (point text)", "Adobe Area Type Tool": "AI.text(str, x, y, {width, height}) (area text)",
    "Adobe Path Type Tool": "AI.textOnPath(path, str)", "Adobe Vertical Type Tool": "AI.text(str, x, y, {vertical: true})",
    "Adobe Vertical Area Type Tool": "areaText + orientation VERTICAL", "Adobe Vertical Path Type Tool": "pathText + orientation VERTICAL",
    "Adobe Touch Type Tool": "characters[i].characterAttributes (size, rotation, baselineShift, horizontalScale)", "Adobe Line Tool": "AI.line(x1, y1, x2, y2)",
    "Adobe Arc Tool": "AI.path with bezier handles (quarter arc)", "Adobe Shape Construction Spiral Tool": "AI.path with computed spiral points",
    "Adobe Rectangular Grid Tool": "loops of AI.line / AI.grid", "Adobe Polar Grid Tool": "AI.circle rings + AI.line spokes",
    "Adobe Rectangle Shape Tool": "AI.rect()", "Adobe Rounded Rectangle Tool": "AI.roundRect()", "Adobe Ellipse Shape Tool": "AI.ellipse() / AI.circle()",
    "Adobe Shape Construction Regular Polygon Tool": "AI.polygon()", "Adobe Shape Construction Star Tool": "AI.star()", "Adobe Flare Tool": "Flare needs a mouse gesture (no DOM)",
    "Adobe Blob Brush Tool": "filled paths: AI.path + Pathfinder unite", "Adobe Brush Tool": "brush.applyTo(path)", "Adobe Freehand Tool": "AI.path(points) (pencil)",
    "Adobe Freehand Smooth Tool": "Object > Path > Smooth", "Adobe Freehand Erase Tool": "pathPoint.remove() / Pathfinder minusFront",
    "Adobe Rotate Tool": "AI.rotate()", "Adobe Reflect Tool": "AI.flip()", "Adobe Scale Tool": "AI.scaleTo() / item.resize()", "Adobe Shear Tool": "item.transform(shear matrix)",
    "Adobe Reshape Tool": "move pathPoints[i].anchor", "Adobe Warp Tool": "AI.warp() / Envelope Distort", "Adobe New Twirl Tool": "Effect > Distort & Transform > Twist (AI.fx)",
    "Adobe Pucker Tool": "Effect > Pucker & Bloat (AI.fx)", "Adobe Bloat Tool": "Effect > Pucker & Bloat (AI.fx)", "Adobe Scallop Tool": "Effect > Zig Zag / Roughen (AI.fx)",
    "Adobe Cyrstallize Tool": "Effect > Roughen (AI.fx)", "Adobe Wrinkle Tool": "Effect > Roughen (AI.fx)", "Adobe Free Transform Tool": "item.transform(matrix) / Effect > Free Distort",
    "Adobe Symbol Sprayer Tool": "loop symbolItems.add(symbol) at positions", "Adobe Symbol Shifter Tool": "symbolItem.translate()", "Adobe Symbol Scruncher Tool": "symbolItem.translate()",
    "Adobe Symbol Sizer Tool": "symbolItem.resize()", "Adobe Symbol Spinner Tool": "symbolItem.rotate()", "Adobe Symbol Stainer Tool": "symbolItem colorize via opacity/blend",
    "Adobe Symbol Screener Tool": "symbolItem.opacity", "Adobe Symbol Styler Tool": "graphicStyle.applyTo(symbolItem)",
    "Adobe Column Graph Tool": "graphs cannot be created by script (tests/fixtures/graph.ai made with the tool)", "Adobe Stacked Column Graph Tool": "graph (fixture)",
    "Adobe Bar Graph Tool": "graph (fixture)", "Adobe Stacked Bar Graph Tool": "graph (fixture)", "Adobe Line Graph Tool": "graph (fixture)", "Adobe Area Graph Tool": "graph (fixture)",
    "Adobe Scatter Graph Tool": "graph (fixture)", "Adobe Pie Graph Tool": "graph (fixture)", "Adobe Radar Graph Tool": "graph (fixture)",
    "Adobe Mesh Editing Tool": "Object > Create Gradient Mesh (menu sweep)", "Adobe Gradient Vector Tool": "AI.gradient() fill + GradientColor.angle / origin",
    "Adobe Eyedropper Tool": "copy colors: target.fillColor = source.fillColor", "Adobe Measure Tool": "AI.box(item) (readback)", "Adobe Blend Tool": "AI.blend()",
    "Adobe Shape Builder Tool": "AI.pathfinder(items, 'unite' | 'divide' …)", "Adobe Planar Paintbucket Tool": "Live Paint (menu sweep); fill via pathfinder divide + fillColor",
    "Adobe Planar Face Select Tool": "Live Paint selection", "Perspective Grid Tool": "document.showPerspectiveGrid()", "Perspective Selection Tool": "Object > Perspective > Attach to Active Plane",
    "Adobe Crop Tool": "artboards: AI.addArtboard() / artboard.artboardRect", "Adobe Slice Tool": "item.sliced = true / Object > Slice", "Adobe Slice Select Tool": "select sliced items",
    "Adobe Eraser Tool": "Pathfinder minusFront with an eraser shape", "Adobe Scissors Tool": "split a path: two AI.path() from its points", "Adobe Knife Tool": "Object > Path > Divide Objects Below",
    "Adobe Scroll Tool": "view: document.activeView.centerPoint", "Adobe Page Tool": "print tiling (no DOM)", "Adobe Zoom Tool": "document.activeView.zoom",
    "Adobe Rotate Canvas Tool": "document.activeView.rotateAngle", "Adobe Width Tool": "variable width profile (no DOM; use stroke + Offset Path)", "Adobe Shaper Tool": "AI.rect/AI.ellipse/AI.polygon + AI.pathfinder",
}

TOOLS = json.loads((SKILL / "index" / "menu-index.json").read_text(encoding="utf-8"))["tools"]
names = [t["tool"] for t in TOOLS if t["tool"] in EQUIV]   # tool-context shortcuts (opacity / blend keys, presentation mode) are not tools
js = (SKILL / "lib" / "json.jsx").read_text(encoding="utf-8") + "var T = " + json.dumps(names) + r""";
if (!app.documents.length) app.documents.add();
var out = [];
for (var i = 0; i < T.length; i++) {
  var r = {tool: T[i]};
  try { app.selectTool(T[i]); r.selected = true; } catch (e) { r.selected = false; r.err = String(e); }
  try { r.got = app.getSelectedToolName(); r.ok = r.got == T[i]; } catch (e) { r.ok = false; r.getErr = String(e); }
  out.push(r);
}
try { app.selectTool('Adobe Select Tool'); } catch (e) {}
J(out);
"""
rows = json.loads(run_js(js, dialog="esc"))
for r in rows:
    r["how"] = EQUIV.get(r["tool"], "")
    r["kind"] = "tool" if r["tool"] in EQUIV else "shortcut"
(HERE / "tools-sweep.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
ok = sum(r["ok"] for r in rows)
for r in rows:
    if not r["ok"] and r["kind"] == "tool":
        print("·", r["tool"], "readback:", r.get("got") or r.get("getErr") or r.get("err"))
tl = [r for r in rows if r["kind"] == "tool"]
print(f"{sum(r['ok'] for r in tl)}/{len(tl)} tools selected and read back; the rest are accepted by selectTool but getSelectedToolName() throws PARM for them "
      f"(it also throws after choosing them with their own keyboard shortcut) -> tests/tools-sweep.json")

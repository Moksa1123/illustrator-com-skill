// Sandbox helpers shared by the sweeps and tests. Coordinates are Illustrator's: y grows upward, rectangle(top, left, w, h).
var TMP = (function () { var f = new Folder(Folder.temp + '/ai_skill_sandbox'); if (!f.exists) f.create(); return f.fullName; })();
function RGB(r, g, b) { var c = new RGBColor(); c.red = r; c.green = g; c.blue = b; return c; }
function CLOSEALL() { while (app.documents.length) app.documents[0].close(SaveOptions.DONOTSAVECHANGES); }
function NEWDOC(w, h, name) {
  var p = new DocumentPreset(); p.width = w || 800; p.height = h || 800; p.colorMode = DocumentColorSpace.RGB; p.units = RulerUnits.Points; p.title = name || '_sandbox';
  var d = app.documents.addDocument('', p);
  try { app.executeMenuCommand('consolidateAllWindows'); } catch (e) {}   // documents must be tabs, not hidden floating windows
  return d;
}
function RECT(t, l, w, h, col, stroke) {
  var r = app.activeDocument.pathItems.rectangle(t, l, w, h); r.filled = true; r.fillColor = col || RGB(220, 40, 40);
  r.stroked = stroke !== false; if (r.stroked) { r.strokeColor = RGB(20, 20, 20); r.strokeWidth = 2; } return r;
}
function ELLIPSE(t, l, w, h, col) { var e = app.activeDocument.pathItems.ellipse(t, l, w, h); e.filled = true; e.fillColor = col || RGB(40, 90, 220); e.stroked = false; return e; }
function TEXT(s, x, y, size) { var t = app.activeDocument.textFrames.pointText([x || 100, y || 200]); t.contents = s || 'Sample Text 123'; t.textRange.characterAttributes.size = size || 36; return t; }
function SEL(a) { app.activeDocument.selection = null; for (var i = 0; i < a.length; i++) a[i].selected = true; }
function SAVEAI(path) {
  var o = new IllustratorSaveOptions(); o.compressed = false; o.pdfCompatible = false; o.embedICCProfile = false;
  for (var i = 0; i < 4; i++) {                        // right after a dialog closes Illustrator can briefly refuse ("No such element")
    try { app.activeDocument.saveAs(new File(path), o); return path; } catch (e) { if (i == 3) throw e; $.sleep(700); app.redraw(); }
  }
}
function PNG(path, scale) {
  var o = new ExportOptionsPNG24(); o.artBoardClipping = true; o.antiAliasing = true; o.transparency = false; o.horizontalScale = o.verticalScale = scale || 50;
  app.activeDocument.exportFile(new File(path), ExportType.PNG24, o); return path;
}
function PNGFILE() { return TMP + '/_pix.png'; }
function DEEP(tag) { return SAVEAI(TMP + '/_d_' + tag + '.ai'); }
function near(a, b, t) { return Math.abs(a - b) <= (t === undefined ? 0.6 : t); }
function SHOT(tag) { return PNG(TMP + '/_p_' + tag + '.png', 100); }

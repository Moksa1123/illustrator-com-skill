// Scenarios for the menu sweep. SETUP(kind) builds a fresh 800x600 document and leaves named items in globals:
//   R red rectangle (selected by default), E blue ellipse overlapping R, T point text, plus per-kind extras.
// Kinds (combine with '+'): sel2 (R+E selected), sel3 (3 rects A1..A3 selected), none (nothing selected), txt (T selected),
//   txtr (text of T selected as a range), txtip (insertion point inside T), area (area text AT selected), pathtxt (path text PT),
//   grp (group G of R+E), img (embedded raster IMG), placed (linked image PL), open2 (two open paths P1 P2 selected),
//   blend (blend BL), env (envelope EN), lp (live paint LP), clip (clip group CG), cmp (compound CP), trace (tracing TR),
//   sym (symbol instance SY), rep (radial repeat RP), grad (gradient-filled GR), cmyk (CMYK document), saved (document saved to TMP),
//   rot (R rotated 30°), guide (a guide GD), black (CMYK black-filled BK), anchors (R with 2 anchors selected), trans (R 50% opacity)
var ZP, R2, T2, T3, SP, BP, D, R, E, T, G, IMG, PL, P1, P2, BL, EN, LP, CG, CP, TR, SY, RP, AT, PT, A1, A2, A3, GR, GD, BK;
function N(name) { try { return app.activeDocument.pageItems.getByName(name); } catch (e) { return null; } }
function NS() { var s = app.activeDocument.selection; return s ? (s.typename == 'TextRange' ? -1 : s.length) : 0; }
function SELT(i) { var s = app.activeDocument.selection; return s && s.length > (i || 0) ? s[i || 0].typename : ''; }
function CNT(k) { return app.activeDocument[k].length; }
function MENU(c) { app.executeMenuCommand(c); }
function has(o, k) { try { return o[k] !== undefined; } catch (e) { return false; } }
function IMGFILE() {
  var f = new File(TMP + '/_sweep_img.png');
  if (!f.exists) { var d0 = app.activeDocument, d = NEWDOC(200, 150, '_imgsrc'); AI.rect(0, 0, 200, 150, {fill: [30, 140, 220], stroke: null}); AI.circle(100, 75, 50, {fill: [240, 200, 30], stroke: null});
    AI.png(f.fsName, {scale: 100}); d.close(SaveOptions.DONOTSAVECHANGES); d0.activate(); }
  return f;
}
function SETUP(kind) {
  CLOSEALL(); kind = kind || '';
  var K = {}; var parts = kind.split('+'); for (var i = 0; i < parts.length; i++) K[parts[i]] = 1;
  if (K.cmyk || K.black) { var p = new DocumentPreset(); p.width = 800; p.height = 600; p.colorMode = DocumentColorSpace.CMYK; p.units = RulerUnits.Points; p.title = '_sandbox'; D = app.documents.addDocument('', p); }
  else D = NEWDOC(800, 600);
  R = AI.rect(100, 100, 200, 150, {fill: [220, 40, 40], stroke: [20, 20, 20], strokeWidth: 2, name: 'R'});
  E = AI.ellipse(220, 180, 200, 150, {fill: [40, 90, 220], stroke: null, name: 'E'});
  T = AI.text('Sample text abc', 100, 400, {size: 36, name: 'T'});
  if (K.sel3) { A1 = AI.rect(450, 80, 40, 40, {fill: [200, 0, 0], name: 'A1'}); A2 = AI.rect(520, 150, 60, 60, {fill: [0, 150, 0], name: 'A2'}); A3 = AI.rect(700, 300, 50, 50, {fill: [0, 0, 200], name: 'A3'}); }
  if (K.area) { AT = AI.text('Area text flows inside a box. Area text flows inside a box. Area text flows inside a box.', 450, 350, {width: 250, height: 150, size: 16, name: 'AT'}); }
  if (K.pathtxt) { var c = AI.circle(600, 150, 80); PT = D.textFrames.pathText(c); PT.contents = 'Text on a path around'; PT.name = 'PT'; }
  if (K.grp) { G = AI.group([R, E], 'G'); }
  if (K.img) { IMG = AI.place(IMGFILE(), 450, 300, {embed: true}); IMG.name = 'IMG'; }
  if (K.placed) { PL = AI.place(IMGFILE(), 450, 300); PL.name = 'PL'; }
  if (K.open2) { P1 = AI.line(450, 100, 550, 100, {name: 'P1', stroke: [0, 0, 0], strokeWidth: 3}); P2 = AI.line(560, 110, 650, 200, {name: 'P2', stroke: [0, 0, 0], strokeWidth: 3}); }
  if (K.blend) { AI.circle(480, 100, 25, {fill: [220, 0, 0], stroke: null, name: 'BLa'}); AI.circle(720, 250, 25, {fill: [0, 0, 220], stroke: null, name: 'BLb'}); }   // made into BL by POST_STEPS
  if (K.env) { AI.rect(450, 350, 200, 100, {fill: [0, 160, 80], name: 'ENsrc'}); }
  if (K.lp) { AI.rect(450, 350, 120, 120, {fill: [240, 180, 0], name: 'LPa'}); AI.circle(580, 410, 60, {fill: [0, 180, 240], name: 'LPb'}); }
  if (K.clip) { var m = AI.circle(200, 175, 60); CG = AI.clip(m, [R]); CG.name = 'CG'; }
  if (K.cmp) { CP = AI.compound([AI.rect(450, 50, 200, 200, {fill: [100, 0, 150]}), AI.rect(500, 100, 100, 100)]); CP.name = 'CP'; }
  if (K.trace) { var ti = AI.place(IMGFILE(), 450, 300, {embed: true}); TR = ti.trace(); TR.name = 'TR'; }
  if (K.sym) { var s0 = AI.star(0, 0, 30, 12, 5, {fill: [220, 120, 0]}); var sy = D.symbols.add(s0); s0.remove(); SY = D.symbolItems.add(sy); AI.moveTo(SY, 500, 100); SY.name = 'SY'; }
  if (K.rep) { AI.circle(600, 150, 15, {fill: [200, 0, 100], name: 'RPsrc'}); }
  if (K.grad) { GR = AI.rect(450, 350, 250, 150, {fill: AI.gradient([[0, [255, 0, 0]], [1, [0, 0, 255]]]), stroke: null, name: 'GR'}); }
  if (K.rot) { R.rotate(30); }
  if (K.guide) { GD = AI.line(50, 550, 750, 550); GD.guides = true; GD.name = 'GD'; }
  if (K.black) { BK = AI.rect(450, 350, 150, 100, {fill: {c: 0, m: 0, y: 0, k: 100}, stroke: null, name: 'BK'}); }
  if (K.trans) { R.opacity = 50; }
  if (K.saved) { SAVEAI(TMP + '/_sweep_saved.ai'); }
  if (!POSTKIND(kind)) SELECTFOR(kind);
  return D;
}
// Object references kept in globals go stale between DoJavaScript calls (they keep reporting old geometry), so every
// call after SETUP re-binds the named sandbox items from the document.
function REBIND() {
  if (!app.documents.length) return;
  D = app.activeDocument;
  var names = ['R', 'E', 'T', 'G', 'IMG', 'PL', 'P1', 'P2', 'BL', 'EN', 'LP', 'CG', 'CP', 'TR', 'SY', 'RP', 'AT', 'PT', 'A1', 'A2', 'A3', 'GR', 'GD', 'BK', 'ZP', 'R2', 'T2', 'T3', 'SP', 'BP'];
  for (var i = 0; i < names.length; i++) { var it = N(names[i]); $.global[names[i]] = it ? it : undefined; }   // never keep an object from an earlier case
}

var POSTKINDS = {blend: 1, env: 1, lp: 1, rep: 1};
function POSTKIND(kind) { var p = (kind || '').split('+'); for (var i = 0; i < p.length; i++) if (POSTKINDS[p[i]]) return true; return false; }
function SELECTFOR(kind) {
  REBIND(); var K = {}; var parts = (kind || '').split('+'); for (var i = 0; i < parts.length; i++) K[parts[i]] = 1;
  D.selection = null;
  if (K.none) {}
  else if (K.sel2) AI.select([R, E]);
  else if (K.sel3) AI.select([A1, A2, A3]);
  else if (K.txt) AI.select([T]);
  else if (K.txtr) T.textRange.select();
  else if (K.txtip) T.textRange.characters[6].select();          // a 1-char selection: insert commands replace it
  else if (K.area) AI.select([AT]);
  else if (K.pathtxt) AI.select([PT]);
  else if (K.grp) AI.select([G]);
  else if (K.img) AI.select([IMG]);
  else if (K.placed) AI.select([PL]);
  else if (K.open2) AI.select([P1, P2]);
  else if (K.blend) AI.select([BL]);
  else if (K.env) { if (EN) AI.select([EN]); }
  else if (K.lp) { if (LP) AI.select([LP]); }
  else if (K.clip) AI.select([CG]);
  else if (K.cmp) AI.select([CP]);
  else if (K.trace) AI.select([TR]);
  else if (K.sym) AI.select([SY]);
  else if (K.rep) { var rr = RP || (D.radialRepeatItems.length ? D.radialRepeatItems[0] : null); if (rr) AI.select([rr]); }
  else if (K.grad) AI.select([GR]);
  else if (K.guide) AI.select([GD]);
  else if (K.black) AI.select([BK]);
  else if (K.anchors) { R.pathPoints[0].selected = PathPointSelection.ANCHORPOINT; R.pathPoints[1].selected = PathPointSelection.ANCHORPOINT; }
  else AI.select([R]);
}

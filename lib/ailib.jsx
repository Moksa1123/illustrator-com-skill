// ailib.jsx — Illustrator design library (ExtendScript). Every function has a test in tests/tests.jsx that reads the
// result back (tests/run_tests.py -> tests/REPORT.md). Only use functions whose test passes on your Illustrator.
// Conventions
//   * Coordinates are artboard-relative, top-left origin, y DOWN, in points (1 pt = 1 px at 72 ppi):
//     AI.rect(x, y, w, h) puts the rectangle's top-left corner x pt right and y pt below the active artboard's top-left.
//   * Colors: [r, g, b] (0-255), '#rrggbb', {c, m, y, k} (0-100), {gray: 0-100}, {spot: 'name', tint: 0-100}, null = none,
//     or any Illustrator Color object.
//   * Style objects: {fill, stroke, strokeWidth, dash: [..], cap: 'butt'|'round'|'square', join: 'miter'|'round'|'bevel',
//     opacity: 0-100, blend: 'multiply'|..., name, layer: 'Layer name'}
//   * Functions return the item they create or change.
var AI = {};
AI.D = function () { return app.activeDocument; };

// ── coordinates ─────────────────────────────────────────────────────────────
AI.ab = function (i) {                                 // artboard rect as {left, top, right, bottom, w, h} in document coords
  var D = AI.D(), A = D.artboards[i === undefined ? D.artboards.getActiveArtboardIndex() : i], r = A.artboardRect;
  return {left: r[0], top: r[1], right: r[2], bottom: r[3], w: r[2] - r[0], h: r[1] - r[3], index: i};
};
AI.pt = function (x, y, i) { var a = AI.ab(i); return [a.left + x, a.top - y]; };       // artboard (x, y-down) -> document point
AI.xy = function (p, i) { var a = AI.ab(i); return [p[0] - a.left, a.top - p[1]]; };     // document point -> artboard (x, y-down)
AI.box = function (item, kind, i) {                    // {x, y, w, h} of an item in artboard coords; kind 'geometric' (default) | 'visible'
  var b = kind == 'visible' ? item.visibleBounds : item.geometricBounds, a = AI.ab(i);
  return {x: b[0] - a.left, y: a.top - b[1], w: b[2] - b[0], h: b[1] - b[3]};
};

// ── colors ──────────────────────────────────────────────────────────────────
AI.rgb = function (r, g, b) { var c = new RGBColor(); c.red = r; c.green = g; c.blue = b; return c; };
AI.cmyk = function (c, m, y, k) { var o = new CMYKColor(); o.cyan = c; o.magenta = m; o.yellow = y; o.black = k; return o; };
AI.gray = function (g) { var o = new GrayColor(); o.gray = g; return o; };
AI.none = function () { return new NoColor(); };
AI.hex = function (h) { h = h.replace('#', ''); if (h.length == 3) h = h.charAt(0) + h.charAt(0) + h.charAt(1) + h.charAt(1) + h.charAt(2) + h.charAt(2);
  return AI.rgb(parseInt(h.substr(0, 2), 16), parseInt(h.substr(2, 2), 16), parseInt(h.substr(4, 2), 16)); };
AI.color = function (v) {
  if (v === null || v === undefined || v === 'none') return AI.none();
  if (typeof v == 'string') return AI.hex(v);
  if (v instanceof Array) return AI.rgb(v[0], v[1], v[2]);
  if (v.typename) return v;
  if (v.spot !== undefined) return AI.spotColor(v.spot, v.color, v.tint);
  if (v.c !== undefined) return AI.cmyk(v.c, v.m, v.y, v.k);
  if (v.gray !== undefined) return AI.gray(v.gray);
  return v;
};
AI.toRGB = function (c) {                              // readback helper: color -> [r, g, b] (RGB documents)
  if (!c) return null;
  if (c.typename == 'RGBColor') return [Math.round(c.red), Math.round(c.green), Math.round(c.blue)];
  if (c.typename == 'SpotColor') return AI.toRGB(c.spot.color);
  if (c.typename == 'GrayColor') { var g = Math.round(255 - c.gray * 2.55); return [g, g, g]; }
  return null;
};
AI.spotColor = function (name, base, tint) {           // spot swatch (created once, reused by name)
  var D = AI.D(), s = null;
  try { s = D.spots.getByName(name); } catch (e) {}
  if (!s) { s = D.spots.add(); s.name = name; s.colorType = ColorModel.SPOT; s.color = AI.color(base || {c: 0, m: 100, y: 100, k: 0}); }
  var c = new SpotColor(); c.spot = s; c.tint = tint === undefined ? 100 : tint; return c;
};
AI.swatch = function (name, color) {                   // named process swatch in the Swatches panel
  var D = AI.D(), s;
  try { s = D.swatches.getByName(name); } catch (e) { s = D.swatches.add(); s.name = name; }
  s.color = AI.color(color); return s;
};
// stops: [[position 0-1, color, opacity 0-100 (optional), midpoint 13-87 (optional)], ...]
AI.gradient = function (stops, opt) {
  opt = opt || {}; var D = AI.D(), g = D.gradients.add();
  if (opt.name) g.name = opt.name;
  g.type = opt.type == 'radial' ? GradientType.RADIAL : GradientType.LINEAR;
  while (g.gradientStops.length < stops.length) g.gradientStops.add();
  for (var i = 0; i < stops.length; i++) {
    var s = g.gradientStops[i]; s.rampPoint = stops[i][0] * 100; s.color = AI.color(stops[i][1]);
    if (stops[i][2] !== undefined) s.opacity = stops[i][2];
    if (stops[i][3] !== undefined) s.midPoint = stops[i][3];
  }
  var c = new GradientColor(); c.gradient = g; if (opt.angle !== undefined) c.angle = opt.angle; return c;
};

// ── style ───────────────────────────────────────────────────────────────────
AI.BLEND = {normal: 'NORMAL', multiply: 'MULTIPLY', screen: 'SCREEN', overlay: 'OVERLAY', softlight: 'SOFTLIGHT', hardlight: 'HARDLIGHT',
  colordodge: 'COLORDODGE', colorburn: 'COLORBURN', darken: 'DARKEN', lighten: 'LIGHTEN', difference: 'DIFFERENCE', exclusion: 'EXCLUSION',
  hue: 'HUE', saturation: 'SATURATIONBLEND', color: 'COLORBLEND', luminosity: 'LUMINOSITY'};
AI.style = function (it, s) {
  if (!s) return it;
  if (it.typename == 'GroupItem') {                      // paint every shape inside (e.g. a pathfinder result); opacity/name stay on the group
    var ps = {}; for (var k in s) if (k != 'opacity' && k != 'name' && k != 'blend' && k != 'layer') ps[k] = s[k];
    for (var j = 0; j < it.pageItems.length; j++) AI.style(it.pageItems[j], ps);
  }
  var paint = it.typename == 'PathItem' ? it : null;
  if (it.typename == 'CompoundPathItem' && it.pathItems.length) paint = it.pathItems[0];
  if (paint) {
    if (s.fill !== undefined) { if (s.fill === null || s.fill === 'none') paint.filled = false; else { paint.filled = true; paint.fillColor = AI.color(s.fill); } }
    if (s.stroke !== undefined) { if (s.stroke === null || s.stroke === 'none') paint.stroked = false; else { paint.stroked = true; paint.strokeColor = AI.color(s.stroke); } }
    if (s.strokeWidth !== undefined) { paint.strokeWidth = s.strokeWidth; if (s.stroke === undefined && !paint.stroked) { paint.stroked = true; } }
    if (s.dash) paint.strokeDashes = s.dash;
    if (s.cap) paint.strokeCap = {butt: StrokeCap.BUTTENDCAP, round: StrokeCap.ROUNDENDCAP, square: StrokeCap.PROJECTINGENDCAP}[s.cap];
    if (s.join) paint.strokeJoin = {miter: StrokeJoin.MITERENDJOIN, round: StrokeJoin.ROUNDENDJOIN, bevel: StrokeJoin.BEVELENDJOIN}[s.join];
  }
  if (it.typename == 'TextFrame') {
    var ca = it.textRange.characterAttributes;
    if (s.fill !== undefined) ca.fillColor = AI.color(s.fill);
    if (s.stroke !== undefined) ca.strokeColor = AI.color(s.stroke);
    if (s.strokeWidth !== undefined) ca.strokeWeight = s.strokeWidth;
  }
  if (s.opacity !== undefined) it.opacity = s.opacity;
  if (s.blend) it.blendingMode = BlendModes[AI.BLEND[s.blend] || s.blend.toUpperCase()];
  if (s.name) it.name = s.name;
  if (s.layer) it.move(AI.layer(s.layer), ElementPlacement.PLACEATBEGINNING);
  return it;
};
AI.layer = function (name, opt) {                      // get or create a top-level layer
  var D = AI.D(), L;
  try { L = D.layers.getByName(name); } catch (e) { L = D.layers.add(); L.name = name; }
  if (opt) { if (opt.locked !== undefined) L.locked = opt.locked; if (opt.visible !== undefined) L.visible = opt.visible; if (opt.printable !== undefined) L.printable = opt.printable;
    if (opt.color) L.color = AI.color(opt.color); if (opt.opacity !== undefined) L.opacity = opt.opacity; }
  return L;
};

// ── shapes (artboard coords, top-left, y down) ──────────────────────────────
// new art goes into the active layer explicitly: document collections insert into a stale target layer
// for the rest of a call that added layers (e.g. the Guides layer of AI.newDoc)
AI.T = function () { return AI.D().activeLayer; };
AI.rect = function (x, y, w, h, s) { var p = AI.pt(x, y); return AI.style(AI.T().pathItems.rectangle(p[1], p[0], w, h), s || {}); };
AI.roundRect = function (x, y, w, h, r, s) { var p = AI.pt(x, y); return AI.style(AI.T().pathItems.roundedRectangle(p[1], p[0], w, h, r, r), s || {}); };
AI.ellipse = function (x, y, w, h, s) { var p = AI.pt(x, y); return AI.style(AI.T().pathItems.ellipse(p[1], p[0], w, h), s || {}); };
AI.circle = function (cx, cy, r, s) { return AI.ellipse(cx - r, cy - r, 2 * r, 2 * r, s); };
AI.polygon = function (cx, cy, r, sides, s) { var p = AI.pt(cx, cy); return AI.style(AI.T().pathItems.polygon(p[0], p[1], r, sides), s || {}); };
AI.star = function (cx, cy, r, inner, points, s) { var p = AI.pt(cx, cy); return AI.style(AI.T().pathItems.star(p[0], p[1], r, inner, points), s || {}); };
AI.line = function (x1, y1, x2, y2, s) {
  var it = AI.T().pathItems.add(); it.setEntirePath([AI.pt(x1, y1), AI.pt(x2, y2)]); it.closed = false; it.filled = false;
  s = s || {}; if (s.stroke === undefined) s.stroke = [0, 0, 0]; if (s.strokeWidth === undefined) s.strokeWidth = 1; return AI.style(it, s);
};
// points: [[x, y], ...] or bezier [[x, y, inX, inY, outX, outY], ...] (handles in artboard coords); opt {closed: true}
AI.path = function (points, s, opt) {
  var it = AI.T().pathItems.add(), anchors = [];
  for (var i = 0; i < points.length; i++) anchors.push(AI.pt(points[i][0], points[i][1]));
  it.setEntirePath(anchors);
  for (i = 0; i < points.length; i++) if (points[i].length >= 6) {
    var P = it.pathPoints[i]; P.leftDirection = AI.pt(points[i][2], points[i][3]); P.rightDirection = AI.pt(points[i][4], points[i][5]); P.pointType = PointType.SMOOTH;
  }
  it.closed = !opt || opt.closed !== false; return AI.style(it, s || {});
};
AI.svgPath = function (d, s) {                          // subset of SVG path data: M L H V C Q Z (absolute + relative)
  var tok = d.match(/[MLHVCQZmlhvcqz]|-?\d*\.?\d+(?:e-?\d+)?/g), i = 0, cmd = '', cx = 0, cy = 0, sx = 0, sy = 0, paths = [], cur = null;
  function n() { return parseFloat(tok[i++]); }
  function add(x, y, ix, iy) { cur.push([x, y, ix === undefined ? x : ix, iy === undefined ? y : iy, x, y]); }
  while (i < tok.length) {
    if (/[A-Za-z]/.test(tok[i])) cmd = tok[i++];
    var rel = cmd == cmd.toLowerCase(), C = cmd.toUpperCase(), ox = rel ? cx : 0, oy = rel ? cy : 0;
    if (C == 'M') { cur = []; paths.push(cur); cx = n() + ox; cy = n() + oy; sx = cx; sy = cy; add(cx, cy); cmd = rel ? 'l' : 'L'; }
    else if (C == 'L') { cx = n() + ox; cy = n() + oy; add(cx, cy); }
    else if (C == 'H') { cx = n() + ox; add(cx, cy); }
    else if (C == 'V') { cy = n() + oy; add(cx, cy); }
    else if (C == 'C') { var x1 = n() + ox, y1 = n() + oy, x2 = n() + ox, y2 = n() + oy; cx = n() + ox; cy = n() + oy; var last = cur[cur.length - 1]; last[4] = x1; last[5] = y1; add(cx, cy, x2, y2); }
    else if (C == 'Q') { var qx = n() + ox, qy = n() + oy, ex = n() + ox, ey = n() + oy, L0 = cur[cur.length - 1];
      L0[4] = L0[0] + 2 / 3 * (qx - L0[0]); L0[5] = L0[1] + 2 / 3 * (qy - L0[1]); add(ex, ey, ex + 2 / 3 * (qx - ex), ey + 2 / 3 * (qy - ey)); cx = ex; cy = ey; }
    else if (C == 'Z') { cur.closed = true; cx = sx; cy = sy; cmd = ''; if (cur.length > 1) { var f = cur[0], l = cur[cur.length - 1]; if (Math.abs(f[0] - l[0]) < 1e-6 && Math.abs(f[1] - l[1]) < 1e-6) { f[2] = l[2]; f[3] = l[3]; cur.pop(); } } }
    else i++;
  }
  var items = [];
  for (var k = 0; k < paths.length; k++) {
    var P = paths[k], pts = [];
    for (var j = 0; j < P.length; j++) pts.push(P[j]);
    items.push(AI.path(pts, {}, {closed: !!P.closed}));
  }
  var out = items.length > 1 ? AI.compound(items) : items[0];
  return AI.style(out, s || {});
};

// ── structure ───────────────────────────────────────────────────────────────
AI.group = function (items, name) {
  function z(it) { var p = it.parent.pageItems; for (var k = 0; k < p.length; k++) if (p[k] == it) return k; return 1e6; }   // 0 = front
  var s = items.slice(0).sort(function (a, b) { return z(a) - z(b); });   // front first (absoluteZOrderPosition throws on new items)
  var g = AI.T().groupItems.add(); if (name) g.name = name;
  g.move(s[0], ElementPlacement.PLACEBEFORE);
  for (var i = 0; i < s.length; i++) s[i].move(g, ElementPlacement.PLACEATEND);   // keeps the stacking order (pathfinder front/back)
  return g;
};
AI.ungroup = function (g) { var out = [], p = g.parent; while (g.pageItems.length) { var it = g.pageItems[0]; it.move(g, ElementPlacement.PLACEBEFORE); out.push(it); } g.remove(); return out; };
AI.clip = function (mask, items) {                     // clipping group: mask shape on top of items
  var g = AI.group([mask].concat(items)); mask.move(g, ElementPlacement.PLACEATBEGINNING); g.clipped = true; mask.clipping = true; return g;
};
AI.compound = function (paths) {                        // compound path (holes where paths overlap by even-odd / nonzero)
  var c = AI.T().compoundPathItems.add(); c.move(paths[0], ElementPlacement.PLACEBEFORE);
  for (var i = paths.length - 1; i >= 0; i--) paths[i].move(c, ElementPlacement.PLACEATBEGINNING);
  for (i = 0; i < c.pathItems.length; i++) c.pathItems[i].evenodd = true;   // overlaps become holes regardless of path direction
  return c;
};
AI.select = function (items) { var D = AI.D(); D.selection = null; for (var i = 0; i < items.length; i++) items[i].selected = true; return items; };
AI.menu = function (cmd, items) { if (items) AI.select(items); app.executeMenuCommand(cmd); return AI.D().selection; };

// ── transforms / layout ─────────────────────────────────────────────────────
AI.moveTo = function (it, x, y, kind) { var b = AI.box(it, kind); it.translate(x - b.x, -(y - b.y)); return it; };
AI.scaleTo = function (it, w, h, keep) {               // resize to w x h (keep: keep aspect, fit inside)
  var b = AI.box(it), sx = w / b.w * 100, sy = (h === undefined ? w / b.w : h / b.h) * 100;
  if (keep) sx = sy = Math.min(sx, h === undefined ? sx : sy);
  it.resize(sx, sy, true, true, true, true, 100, Transformation.TOPLEFT); return it;
};
AI.rotate = function (it, deg, anchor) { it.rotate(deg, true, true, true, true, anchor || Transformation.CENTER); return it; };
AI.flip = function (it, dir) { it.resize(dir == 'v' ? 100 : -100, dir == 'v' ? -100 : 100, true, true, true, true, 100, Transformation.CENTER); return it; };
// how: left | hcenter | right | top | vcenter | bottom; to: 'artboard' | 'selection' (default) | a key item
AI.align = function (items, how, to, kind) {
  var R;
  if (to == 'artboard') { var a = AI.ab(); R = {x: 0, y: 0, w: a.w, h: a.h}; }
  else if (to && to.typename) R = AI.box(to, kind);
  else { var x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
    for (var i = 0; i < items.length; i++) { var b = AI.box(items[i], kind); x0 = Math.min(x0, b.x); y0 = Math.min(y0, b.y); x1 = Math.max(x1, b.x + b.w); y1 = Math.max(y1, b.y + b.h); }
    R = {x: x0, y: y0, w: x1 - x0, h: y1 - y0}; }
  for (i = 0; i < items.length; i++) {
    if (to && to.typename && items[i] === to) continue;
    var B = AI.box(items[i], kind), dx = 0, dy = 0;
    if (how == 'left') dx = R.x - B.x; else if (how == 'right') dx = R.x + R.w - B.x - B.w; else if (how == 'hcenter') dx = R.x + R.w / 2 - B.x - B.w / 2;
    else if (how == 'top') dy = R.y - B.y; else if (how == 'bottom') dy = R.y + R.h - B.y - B.h; else if (how == 'vcenter') dy = R.y + R.h / 2 - B.y - B.h / 2;
    items[i].translate(dx, -dy);
  }
  return items;
};
// axis 'h' | 'v'; opt.gap = fixed spacing (otherwise equal spacing between the outermost items)
AI.distribute = function (items, axis, opt) {
  opt = opt || {}; var h = axis != 'v', L = items.slice(0);
  L.sort(function (p, q) { var a = AI.box(p, opt.kind), b = AI.box(q, opt.kind); return h ? a.x - b.x : a.y - b.y; });
  var tot = 0, i, first = AI.box(L[0], opt.kind), last = AI.box(L[L.length - 1], opt.kind);
  for (i = 0; i < L.length; i++) { var b = AI.box(L[i], opt.kind); tot += h ? b.w : b.h; }
  var gap = opt.gap !== undefined ? opt.gap : ((h ? last.x + last.w - first.x : last.y + last.h - first.y) - tot) / (L.length - 1);
  var pos = h ? first.x : first.y;
  for (i = 0; i < L.length; i++) { var B = AI.box(L[i], opt.kind); if (h) L[i].translate(pos - B.x, 0); else L[i].translate(0, -(pos - B.y)); pos += (h ? B.w : B.h) + gap; }
  return L;
};
AI.grid = function (items, cols, gapX, gapY, x, y) {   // lay items out in a grid starting at (x, y)
  var row = 0, col = 0, rowH = 0, cx = x || 0, cy = y || 0;
  for (var i = 0; i < items.length; i++) {
    var b = AI.box(items[i]); AI.moveTo(items[i], cx, cy); rowH = Math.max(rowH, b.h); cx += b.w + (gapX || 0);
    if (++col == cols) { col = 0; row++; cx = x || 0; cy += rowH + (gapY || 0); rowH = 0; }
  }
  return items;
};

// ── text ────────────────────────────────────────────────────────────────────
AI.font = function (name) {                            // TextFont by PostScript name, full name or 'Family Style'; null if missing
  try { return app.textFonts.getByName(name); } catch (e) {}
  var n = name.toLowerCase().replace(/[\s-]/g, '');
  for (var i = 0; i < app.textFonts.length; i++) { var f = app.textFonts[i];
    if ((f.family + f.style).toLowerCase().replace(/[\s-]/g, '') == n || f.name.toLowerCase().replace(/[\s-]/g, '') == n) return f; }
  return null;
};
AI.JUST = {left: 'LEFT', center: 'CENTER', right: 'RIGHT', justify: 'FULLJUSTIFYLASTLINELEFT', justifyAll: 'FULLJUSTIFY'};
// opt: {font, size, color, tracking, leading, align, width, height (area text), vertical, caps: 'all'|'small', hscale, vscale,
//       baseline, rotation, underline, strike, ligatures, kerning: 'auto'|'optical'|'metrics', language}
AI.textAttrs = function (range, o) {
  var ca = range.characterAttributes;
  if (o.font) { var f = typeof o.font == 'string' ? AI.font(o.font) : o.font; if (f) ca.textFont = f; }
  if (o.size !== undefined) ca.size = o.size;
  if (o.color !== undefined) ca.fillColor = AI.color(o.color);
  if (o.stroke !== undefined) ca.strokeColor = AI.color(o.stroke);
  if (o.strokeWidth !== undefined) ca.strokeWeight = o.strokeWidth;
  if (o.tracking !== undefined) ca.tracking = o.tracking;
  if (o.leading !== undefined) { ca.autoLeading = false; ca.leading = o.leading; }
  if (o.hscale !== undefined) ca.horizontalScale = o.hscale;
  if (o.vscale !== undefined) ca.verticalScale = o.vscale;
  if (o.baseline !== undefined) ca.baselineShift = o.baseline;
  if (o.rotation !== undefined) ca.rotation = o.rotation;
  if (o.caps) ca.capitalization = {all: FontCapsOption.ALLCAPS, small: FontCapsOption.SMALLCAPS, allSmall: FontCapsOption.ALLSMALLCAPS, normal: FontCapsOption.NORMALCAPS}[o.caps];
  if (o.underline !== undefined) ca.underline = o.underline;
  if (o.strike !== undefined) ca.strikeThrough = o.strike;
  if (o.ligatures !== undefined) ca.ligature = o.ligatures;
  if (o.kerning) ca.kerningMethod = {auto: AutoKernType.AUTO, optical: AutoKernType.OPTICAL, metrics: AutoKernType.METRICSROMANONLY, none: AutoKernType.NOAUTOKERN}[o.kerning];
  if (o.set) for (var k in o.set) ca[k] = o.set[k];     // any other characterAttributes field (see: ai_api.py class CharacterAttributes)
  if (o.align) range.paragraphAttributes.justification = Justification[AI.JUST[o.align] || o.align.toUpperCase()];
  return range;
};
AI.text = function (str, x, y, o) {
  o = o || {}; var D = AI.D(), t;
  if (o.width) { var p = AI.pt(x, y), box = D.activeLayer.pathItems.rectangle(p[1], p[0], o.width, o.height || 1000); t = D.activeLayer.textFrames.areaText(box); }
  else { t = D.activeLayer.textFrames.pointText(AI.pt(x, y)); }
  t.contents = str;
  if (o.vertical) t.orientation = TextOrientation.VERTICAL;
  AI.textAttrs(t.textRange, o);
  if (!o.width && o.anchor != 'baseline') {             // point text: put the TOP of the text box at y (like CSS), not the baseline
    var b = AI.box(t); t.translate(0, -(y - b.y));
  }
  if (o.name) t.name = o.name;
  return t;
};
// runs: [{t: 'Hello ', size: 40, color: [...], font: '...'}, {t: 'world', ...}] -> one frame with mixed styles
AI.runs = function (frame, runs) {
  var s = ''; for (var i = 0; i < runs.length; i++) s += runs[i].t; frame.contents = s;
  var pos = 0;
  for (i = 0; i < runs.length; i++) {
    var n = runs[i].t.length; if (!n) continue;
    var rng = frame.textRange.characters[pos]; rng.length = n; AI.textAttrs(rng, runs[i]); pos += n;
  }
  return frame;
};
AI.textOnPath = function (path, str, o) { var t = AI.T().textFrames.pathText(path); t.contents = str; AI.textAttrs(t.textRange, o || {}); return t; };
AI.outline = function (frame) { return frame.createOutline(); };
AI.fitText = function (frame, maxW, minSize) {         // shrink a point-text frame until it is at most maxW wide
  var ca = frame.textRange.characterAttributes, s = ca.size;
  while (AI.box(frame).w > maxW && s > (minSize || 4)) { s -= 0.5; frame.textRange.characterAttributes.size = s; }
  return frame;
};
AI.charStyle = function (name, attrs) {
  var D = AI.D(), cs; try { cs = D.characterStyles.getByName(name); } catch (e) { cs = D.characterStyles.add(name); }
  AI.textAttrs({characterAttributes: cs.characterAttributes, paragraphAttributes: {}}, attrs || {}); return cs;
};
AI.paraStyle = function (name, attrs) {
  var D = AI.D(), ps; try { ps = D.paragraphStyles.getByName(name); } catch (e) { ps = D.paragraphStyles.add(name); }
  var o = attrs || {}; AI.textAttrs({characterAttributes: ps.characterAttributes, paragraphAttributes: ps.paragraphAttributes}, o);
  var pa = ps.paragraphAttributes;
  if (o.spaceBefore !== undefined) pa.spaceBefore = o.spaceBefore; if (o.spaceAfter !== undefined) pa.spaceAfter = o.spaceAfter;
  if (o.indent !== undefined) pa.firstLineIndent = o.indent;
  return ps;
};

// ── live effects (dialog-free) ──────────────────────────────────────────────
// AI.fx(item, 'Adobe Drop Shadow', {horz: 4, vert: 4, blur: 6, opac: 0.4}) — name = LiveEffect name, params override defaults.
// Defaults and parameter types for every effect come from presets/effects.json (tests/effects_sweep.py, verified by readback);
// tools/ai_run helpers inject them as AI.FXDB. Without FXDB the params you pass are used as-is (numbers -> R, true/false -> B).
AI.FXDB = AI.FXDB || {};
AI.fxXML = function (name, params) {
  var db = AI.FXDB[name] || {p: {}, t: {}}, P = {}, k, parts = [];
  for (k in db.p) P[k] = db.p[k];
  for (k in params) P[k] = params[k];
  for (k in P) {
    if (k.indexOf(' ') >= 0 || k == 'DisplayString') continue;
    var t = db.t[k] || (typeof P[k] == 'boolean' ? 'Bool' : (Math.round(P[k]) === P[k] && db.t[k] == 'Int') ? 'Int' : 'Real');
    if (t != 'Real' && t != 'Int' && t != 'Bool') continue;
    var v = P[k]; if (t == 'Bool') v = v ? 1 : 0; if (t == 'Int') v = Math.round(v);
    parts.push({Real: 'R', Int: 'I', Bool: 'B'}[t] + ' ' + k + ' ' + v);
  }
  return '<LiveEffect name="' + name + '"><Dict data="' + parts.join(' ') + ' "/></LiveEffect>';
};
AI.fx = function (it, name, params) { it.applyEffect(name.charAt(0) == '<' ? name : AI.fxXML(name, params || {})); return it; };
// friendly wrappers (units: points; opacity 0-1)
AI.dropShadow = function (it, o) { o = o || {}; return AI.fx(it, 'Adobe Drop Shadow', {horz: o.x === undefined ? 4 : o.x, vert: o.y === undefined ? 4 : o.y, blur: o.blur === undefined ? 5 : o.blur, opac: o.opacity === undefined ? 0.5 : o.opacity, dark: o.darkness === undefined ? 100 : o.darkness, blnd: o.blend === undefined ? 1 : o.blend}); };
AI.outerGlow = function (it, o) { o = o || {}; return AI.fx(it, 'Adobe Outer Glow', {blur: o.blur === undefined ? 8 : o.blur, opac: o.opacity === undefined ? 0.75 : o.opacity}); };
AI.innerGlow = function (it, o) { o = o || {}; return AI.fx(it, 'Adobe Inner Glow', {blur: o.blur === undefined ? 8 : o.blur, opac: o.opacity === undefined ? 0.75 : o.opacity}); };
AI.feather = function (it, r) { return AI.fx(it, 'Adobe Fuzzy Mask', {Radius: r === undefined ? 5 : r}); };
AI.roundCorners = function (it, r) { return AI.fx(it, 'Adobe Round Corners', {radius: r === undefined ? 10 : r}); };
AI.offsetPath = function (it, d, join) { return AI.fx(it, 'Adobe Offset Path', {ofst: d, jntp: join === undefined ? 2 : join, mlim: 4}); };
AI.gaussianBlur = function (it, r) { return AI.fx(it, 'Adobe PSL Gaussian Blur', {blur: r === undefined ? 5 : r}); };
// warp styles: 1 arc, 2 arc lower, 3 arc upper, 4 arch, 5 bulge, 6 shell lower, 7 shell upper, 8 flag, 9 wave, 10 fish, 11 rise, 12 fisheye, 13 inflate, 14 squeeze, 15 twist
AI.warp = function (it, style, bend, vertical) { return AI.fx(it, 'Adobe Deform', {DeformStyle: style || 1, DeformValue: bend === undefined ? 0.5 : bend, DeformHoriz: 0, DeformVert: 0, Rotate: !!vertical}); };
AI.roughen = function (it, size, detail) { return AI.fx(it, 'Adobe Roughen', {size: size === undefined ? 5 : size, dtal: detail === undefined ? 10 : detail}); };
AI.expandAppearance = function (it) { AI.select([it]); app.executeMenuCommand('expandStyle'); var s = AI.D().selection; return s.length == 1 ? s[0] : s; };

// ── pathfinder (destructive, like the Pathfinder panel) ────────────────────
// op: unite | intersect | exclude | minusFront | minusBack | divide | trim | merge | crop | outline
AI.PF = {unite: 'Live Pathfinder Add', intersect: 'Live Pathfinder Intersect', exclude: 'Live Pathfinder Exclude', minusFront: 'Live Pathfinder Subtract',
  minusBack: 'Live Pathfinder Minus Back', divide: 'Live Pathfinder Divide', trim: 'Live Pathfinder Trim', merge: 'Live Pathfinder Merge',
  crop: 'Live Pathfinder Crop', outline: 'Live Pathfinder Outline'};
AI.pathfinder = function (items, op) {
  var g = AI.group(items); AI.select([g]); app.executeMenuCommand(AI.PF[op] || op); app.executeMenuCommand('expandStyle');
  var s = AI.D().selection, out = s.length == 1 ? s[0] : s;
  if (out.typename == 'GroupItem' && out.pageItems.length == 1 && op != 'divide' && op != 'trim' && op != 'merge' && op != 'crop' && op != 'outline') {
    var only = out.pageItems[0]; only.move(out, ElementPlacement.PLACEBEFORE); out.remove(); AI.select([only]); out = only;   // one shape: return it, not its wrapper group
  }
  return out;
};

// ── images, symbols, styles ─────────────────────────────────────────────────
// opt: {w, h (fit inside, keep aspect), embed: true, name}
AI.place = function (file, x, y, opt) {
  opt = opt || {}; var p = AI.T().placedItems.add(); p.file = file instanceof File ? file : new File(file);
  if (opt.w) AI.scaleTo(p, opt.w, opt.h || opt.w * p.height / p.width, true);
  AI.moveTo(p, x || 0, y || 0);
  if (opt.name) p.name = opt.name;
  if (opt.embed) { var n = AI.D().rasterItems.length; p.embed(); return AI.D().rasterItems.length > n ? AI.D().rasterItems[0] : p; }
  return p;
};
AI.trace = function (placedOrRaster, preset, expand) {   // Image Trace (preset name from app.tracingPresetsList); expand: return paths
  var t = placedOrRaster.trace(); if (preset) t.tracing.tracingOptions.loadFromPreset(preset);
  t.tracing.tracingOptions.tracingMode; app.redraw();
  return expand ? t.tracing.expandTracing() : t;
};
AI.symbol = function (item, name) { var s = AI.D().symbols.add(item); if (name) s.name = name; return s; };
AI.placeSymbol = function (sym, x, y) { var s = typeof sym == 'string' ? AI.D().symbols.getByName(sym) : sym, it = AI.T().symbolItems.add(s); AI.moveTo(it, x || 0, y || 0); return it; };
AI.graphicStyle = function (it, name) { AI.D().graphicStyles.getByName(name).applyTo(it); return it; };
AI.rasterize = function (it, o) {
  o = o || {}; var r = new RasterizeOptions(); r.resolution = o.resolution || 150; r.antiAliasingMethod = AntiAliasingMethod.ARTOPTIMIZED;
  r.transparency = o.transparent !== false; if (o.padding !== undefined) r.padding = o.padding;
  return AI.D().rasterize(it, it.visibleBounds, r);
};
AI.repeat = function (it, kind) {                       // 'radial' | 'grid' | 'mirror' (Object > Repeat)
  kind = kind || 'radial'; var C = {radial: 'radialRepeatItems', grid: 'gridRepeatItems', mirror: 'symmetryRepeatItems'}[kind], D = AI.D(), n0 = D[C].length;
  AI.select([it]); app.executeMenuCommand({radial: 'Make Radial Repeat', grid: 'Make Grid Repeat', mirror: 'Make Symmetry Repeat'}[kind]);
  var s = D.selection; if (s && s.length && /Repeat/.test(s[0].typename)) return s[0];
  return D[C].length > n0 ? D[C][0] : null;                                   // mirror leaves nothing selected
};
AI.blend = function (items) { AI.select(items); app.executeMenuCommand('Path Blend Make'); return AI.D().selection[0]; };

// ── document ────────────────────────────────────────────────────────────────
// AI.newDoc(1080, 1080, 'post', {mode: 'RGB'|'CMYK', units: 'px'|'pt'|'mm', artboards: 1, spacing: 40, bleed: 0,
//            safe: [l, t, r, b], bg: color, margin: 0})  -> safe-zone guides on a locked 'Guides' layer, bg on locked 'Background'
AI.newDoc = function (w, h, name, o) {
  o = o || {}; var p = new DocumentPreset();
  p.width = w; p.height = h; p.title = name || 'Untitled'; p.numArtboards = o.artboards || 1; p.artboardSpacing = o.spacing || 40;
  p.colorMode = o.mode == 'CMYK' ? DocumentColorSpace.CMYK : DocumentColorSpace.RGB;
  p.units = {px: RulerUnits.Pixels, pt: RulerUnits.Points, mm: RulerUnits.Millimeters, cm: RulerUnits.Centimeters, 'in': RulerUnits.Inches}[o.units || 'px'];
  p.rasterResolution = o.mode == 'CMYK' ? DocumentRasterResolution.HighResolution : DocumentRasterResolution.ScreenResolution;
  if (o.bleed) p.documentBleedOffset = [o.bleed, o.bleed, o.bleed, o.bleed];
  var D = app.documents.addDocument('', p), art = D.layers[0];   // '' = no startup profile (profile names are localized)
  if (o.bg !== undefined) { var L = AI.layer('Background'); L.zOrder(ZOrderMethod.SENDTOBACK);
    for (var i = 0; i < D.artboards.length; i++) { D.artboards.setActiveArtboardIndex(i); var a = AI.ab(i); AI.style(D.pathItems.rectangle(a.top, a.left, a.w, a.h), {fill: o.bg, stroke: null, name: 'bg'}).move(L, ElementPlacement.PLACEATEND); }
    L.locked = true; D.artboards.setActiveArtboardIndex(0); }
  if (o.safe || o.margin) { var s = o.safe || [o.margin, o.margin, o.margin, o.margin];
    for (i = 0; i < D.artboards.length; i++) AI.safeGuides(i, s); }
  D.activeLayer = art;                                       // new layers become active: draw on the artwork layer, not a locked helper layer
  return D;
};
AI.safeGuides = function (i, s) {                      // guides at safe-zone insets [left, top, right, bottom] of artboard i
  var D = AI.D(), prev = D.activeLayer, L = AI.layer('Guides'), a = AI.ab(i), out = [];
  L.locked = false;
  function g(x1, y1, x2, y2) { var it = L.pathItems.add(); it.setEntirePath([[x1, y1], [x2, y2]]); it.guides = true; it.locked = true; out.push(it); }
  if (s[0]) g(a.left + s[0], a.top + 200, a.left + s[0], a.bottom - 200);
  if (s[2]) g(a.right - s[2], a.top + 200, a.right - s[2], a.bottom - 200);
  if (s[1]) g(a.left - 200, a.top - s[1], a.right + 200, a.top - s[1]);
  if (s[3]) g(a.left - 200, a.bottom + s[3], a.right + 200, a.bottom + s[3]);
  if (prev != L) D.activeLayer = prev;   // lock the guides, not the layer: a locked layer stays the insertion target and new art fails with 8705
  return out;
};
AI.addArtboard = function (x, y, w, h, name) {        // x, y relative to artboard 0
  var a = AI.ab(0), D = AI.D(), A = D.artboards.add([a.left + x, a.top - y, a.left + x + w, a.top - y - h]); if (name) A.name = name; return A;
};
AI.fitArtboard = function (i, items) {                  // resize artboard i to the bounds of items (or all art)
  var D = AI.D(); D.artboards.setActiveArtboardIndex(i || 0);
  if (items) { AI.select(items); try { D.fitArtboardToSelectedArt(i || 0); } catch (e) { app.redraw(); AI.select(items); D.fitArtboardToSelectedArt(i || 0); } } else   // the fresh selection is sometimes not a target yet (error 129): redraw + retry { D.selection = null; app.executeMenuCommand('Fit Artboard to artwork bounds'); }
  return D.artboards[i || 0];
};

// ── export ──────────────────────────────────────────────────────────────────
// scale in percent; artboard index (exports only that artboard via exportFile's artBoardClipping on the active artboard)
AI._ab = function (i) { if (i !== undefined) AI.D().artboards.setActiveArtboardIndex(i); };
AI.png = function (path, o) {
  o = o || {}; AI._ab(o.artboard); var e = new ExportOptionsPNG24(); e.artBoardClipping = true; e.antiAliasing = o.antialias !== false;
  e.transparency = !!o.transparent; e.horizontalScale = e.verticalScale = o.scale || 100; AI.D().exportFile(new File(path), ExportType.PNG24, e); return new File(path);
};
AI.jpg = function (path, o) {
  o = o || {}; AI._ab(o.artboard); var e = new ExportOptionsJPEG(); e.artBoardClipping = true; e.antiAliasing = true; e.qualitySetting = o.quality || 85;
  e.horizontalScale = e.verticalScale = o.scale || 100; AI.D().exportFile(new File(path), ExportType.JPEG, e); return new File(path);
};
AI.svg = function (path, o) {                          // web-optimized SVG; o.outlineText converts text to paths in the file only
  o = o || {}; AI._ab(o.artboard); var e = new ExportOptionsWebOptimizedSVG(); e.artboardRange = String((o.artboard || 0) + 1);
  e.fontType = o.outlineText ? SVGFontType.OUTLINEFONT : SVGFontType.SVGFONT; e.rasterImageLocation = RasterImageLocation.EMBED;
  e.coordinatePrecision = o.precision || 2; AI.D().exportFile(new File(path), ExportType.WOSVG, e); return new File(path);
};
AI.webp = function (path, o) {
  o = o || {}; AI._ab(o.artboard); var e = new ExportOptionsWebP(); e.artBoardClipping = true; e.lossy = o.lossless ? false : true; e.quality = o.quality || 85;
  e.horizontalScale = e.verticalScale = o.scale || 100; e.transparency = !!o.transparent; AI.D().exportFile(new File(path), ExportType.WEBP, e); return new File(path);
};
AI.pdf = function (path, o) {                          // o.preset e.g. '[High Quality Print]' / '[Press Quality]'; o.range '1-2'
  o = o || {}; var e = new PDFSaveOptions(); if (o.preset) e.pDFPreset = AI.pdfPreset(o.preset); if (o.range) e.artboardRange = o.range;
  e.preserveEditability = !!o.editable; if (o.bleed) e.bleedLink = true;
  var D = AI.D(), keep = D.fullName; D.saveAs(new File(path), e); return new File(path);
};
AI.PDF_ALIASES = {'high quality print': 1, 'press quality': 6, 'smallest file size': 8, 'illustrator default': 0};   // index in app.PDFPresetsList (names are localized)
AI.pdfPreset = function (name) {                          // exact name, alias of the standard English name, or substring
  var L = app.PDFPresetsList, n = name.replace(/[\[\]]/g, '').toLowerCase();
  for (var i = 0; i < L.length; i++) if (L[i] == name) return L[i];
  if (AI.PDF_ALIASES[n] !== undefined && L.length > 8) return L[AI.PDF_ALIASES[n]];
  for (i = 0; i < L.length; i++) if (L[i].toLowerCase().indexOf(n) >= 0) return L[i];
  throw new Error('PDF preset not found: ' + name + ' (have: ' + L.join(', ') + ')');
};
AI.psd = function (path, o) {
  o = o || {}; var e = new ExportOptionsPhotoshop(); e.resolution = o.resolution || 72; e.editableText = true; e.maximumEditability = true; e.writeLayers = o.layers !== false;
  e.antiAliasing = true; e.artBoardClipping = true; AI.D().exportFile(new File(path), ExportType.PHOTOSHOP, e); return new File(path);
};
AI.saveAI = function (path, o) {
  o = o || {}; var e = new IllustratorSaveOptions(); e.pdfCompatible = o.pdfCompatible !== false; e.compressed = o.compressed !== false;
  AI.D().saveAs(new File(path), e); return new File(path);
};
// every artboard in several formats/scales in one call (Export for Screens). formats: png | jpg | svg | pdf | webp
AI.exportScreens = function (folder, o) {
  o = o || {}; var F = new Folder(folder); if (!F.exists) F.create();
  var it = new ExportForScreensItemToExport(); it.artboards = o.artboards || 'all'; it.document = false;
  var fm = o.formats || ['png'];
  for (var i = 0; i < fm.length; i++) {
    var t, opt;
    if (fm[i] == 'png') { t = ExportForScreensType.SE_PNG24; opt = new ExportForScreensOptionsPNG24(); opt.scaleType = ExportForScreensScaleType.SCALEBYFACTOR; opt.scaleTypeValue = o.scale || 1; }
    else if (fm[i] == 'jpg') { t = ExportForScreensType.SE_JPEG80; opt = new ExportForScreensOptionsJPEG(); opt.scaleType = ExportForScreensScaleType.SCALEBYFACTOR; opt.scaleTypeValue = o.scale || 1; }
    else if (fm[i] == 'svg') { t = ExportForScreensType.SE_SVG; opt = new ExportForScreensOptionsWebOptimizedSVG(); }
    else if (fm[i] == 'pdf') { t = ExportForScreensType.SE_PDF; opt = new ExportForScreensPDFOptions(); }
    else if (fm[i] == 'webp') { t = ExportForScreensType.SE_WEBP; opt = new ExportForScreensOptionsWebP(); opt.scaleType = ExportForScreensScaleType.SCALEBYFACTOR; opt.scaleTypeValue = o.scale || 1; }
    AI.D().exportForScreens(F, t, opt, it, o.prefix || '');
  }
  return F;
};

// ── find / replace / recolor ────────────────────────────────────────────────
AI.findText = function (str, doc) {                     // [{frame, index}] for every occurrence in every text frame
  var D = doc || AI.D(), out = [];
  for (var i = 0; i < D.textFrames.length; i++) { var c = D.textFrames[i].contents, k = c.indexOf(str);
    while (k >= 0) { out.push({frame: D.textFrames[i], index: k}); k = c.indexOf(str, k + str.length); } }
  return out;
};
AI.replaceText = function (find, repl, doc) {          // replaces in place; each occurrence keeps the style of its first character
  var hits = AI.findText(find, doc), n = 0;
  for (var i = hits.length - 1; i >= 0; i--) {
    var r = hits[i].frame.characters[hits[i].index]; r.length = find.length; r.contents = repl; n++;
  }
  return n;
};
// pairs: [[fromColor, toColor], ...] (colors in any AI.color form); tol = max channel difference (RGB)
AI.recolor = function (items, pairs, tol) {
  tol = tol === undefined ? 2 : tol; var n = 0;
  function same(c, f) { var a = AI.toRGB(c), b = AI.toRGB(AI.color(f)); if (!a || !b) return false; return Math.abs(a[0] - b[0]) <= tol && Math.abs(a[1] - b[1]) <= tol && Math.abs(a[2] - b[2]) <= tol; }
  function walk(it) {
    if (it.typename == 'GroupItem') { for (var i = 0; i < it.pageItems.length; i++) walk(it.pageItems[i]); return; }
    if (it.typename == 'CompoundPathItem') { for (i = 0; i < it.pathItems.length; i++) walk(it.pathItems[i]); return; }
    if (it.typename == 'TextFrame') { for (i = 0; i < it.characters.length; i++) { var ca = it.characters[i].characterAttributes;
      for (var p = 0; p < pairs.length; p++) { if (same(ca.fillColor, pairs[p][0])) { ca.fillColor = AI.color(pairs[p][1]); n++; } } } return; }
    if (it.typename != 'PathItem') return;
    for (var q = 0; q < pairs.length; q++) {
      if (it.filled && same(it.fillColor, pairs[q][0])) { it.fillColor = AI.color(pairs[q][1]); n++; break; }
    }
    for (q = 0; q < pairs.length; q++) {
      if (it.stroked && same(it.strokeColor, pairs[q][0])) { it.strokeColor = AI.color(pairs[q][1]); n++; break; }
    }
  }
  for (var i = 0; i < items.length; i++) walk(items[i]);
  return n;
};

// ── headline / threading ────────────────────────────────────────────────────
// Type > Fit Headline for area text: the largest tracking that keeps the paragraph on one line of the frame.
AI.fitHeadline = function (frame, maxTracking) {
  var lo = -100, hi = maxTracking || 2000, ca = frame.textRange.characterAttributes;
  for (var i = 0; i < 14; i++) {
    var mid = Math.round((lo + hi) / 2); ca.tracking = mid; app.redraw();
    if (frame.lines.length <= 1) lo = mid; else hi = mid;
  }
  ca.tracking = lo; return frame;
};
AI.thread = function (a, b) { a.nextFrame = b; return a; };     // Type > Threaded Text > Create (b: empty area-text frame)

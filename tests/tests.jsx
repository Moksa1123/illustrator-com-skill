// ailib tests. Each test runs in a fresh 800x600 pt sandbox document and must READ BACK what it changed.
// A test throws on failure, or returns a message string, or {msg, px: [[x, y, [r,g,b], tol], ...], png: 1, fx: ['Adobe ...'], files: [...]}:
//   px  -> run_tests.py exports the artboard to PNG (1 px = 1 pt) and samples those pixels
//   fx  -> run_tests.py saves an uncompressed .ai and requires those live effects (tools/ai_dump.py)
//   files -> each path must exist with size > 0 (and images must decode)
function A(ok, msg) { if (!ok) throw new Error('assert: ' + msg); }
function near(a, b, t) { return Math.abs(a - b) <= (t === undefined ? 0.6 : t); }
function Bx(it) { var b = AI.box(it); return [Math.round(b.x * 10) / 10, Math.round(b.y * 10) / 10, Math.round(b.w * 10) / 10, Math.round(b.h * 10) / 10]; }
var RED = [220, 30, 30], BLUE = [30, 60, 220], GREEN = [20, 170, 60], WHITE = [255, 255, 255];

var TESTS = [
  // ── coordinates / shapes
  {cat: 'shapes', name: 'rect at artboard top-left coords', fn: function () {
    var r = AI.rect(100, 50, 200, 120, {fill: RED, stroke: null}); var b = Bx(r);
    A(b.join() == '100,50,200,120', 'box ' + b); return {msg: 'AI.box = ' + b.join(','), px: [[150, 100, RED, 10], [90, 100, WHITE, 10], [150, 40, WHITE, 10]]}; }},
  {cat: 'shapes', name: 'roundRect / ellipse / circle / polygon / star', fn: function () {
    var a = AI.roundRect(20, 20, 160, 100, 30, {fill: BLUE}), e = AI.ellipse(220, 20, 160, 100, {fill: GREEN}), c = AI.circle(500, 70, 50, {fill: RED}),
      p = AI.polygon(650, 70, 50, 6, {fill: BLUE}), s = AI.star(150, 300, 80, 35, 5, {fill: GREEN});
    A(a.pathPoints.length == 8, 'roundRect points ' + a.pathPoints.length); A(e.pathPoints.length == 4, 'ellipse'); A(p.pathPoints.length == 6, 'hexagon'); A(s.pathPoints.length == 10, 'star');
    A(near(AI.box(c).w, 100) && near(AI.box(c).x, 450), 'circle ' + Bx(c));
    return {msg: 'rounded corners 8 pts, hexagon 6, star 10, circle 100x100 at 450,20', px: [[22, 22, WHITE, 10], [100, 70, BLUE, 12], [500, 70, RED, 12], [150, 300, GREEN, 12]]}; }},
  {cat: 'shapes', name: 'line with stroke style (dash, cap)', fn: function () {
    var l = AI.line(50, 100, 750, 100, {stroke: RED, strokeWidth: 8, dash: [20, 10], cap: 'round'});
    A(!l.closed && l.stroked && near(l.strokeWidth, 8) && l.strokeDashes.length == 2 && l.strokeCap == StrokeCap.ROUNDENDCAP, 'stroke');
    return {msg: '8 pt dashed [20,10], round caps', px: [[60, 100, RED, 15]]}; }},
  {cat: 'shapes', name: 'bezier path + SVG path data', fn: function () {
    var p = AI.path([[100, 300, 100, 300, 150, 200], [300, 300, 250, 200, 300, 300]], {fill: BLUE}, {closed: true});
    A(p.pathPoints[0].pointType == PointType.SMOOTH, 'smooth'); var sp = AI.svgPath('M400 100 L600 100 L500 250 Z M480 130 L520 130 L500 170 Z', {fill: RED});
    A(sp.typename == 'CompoundPathItem' && sp.pathItems.length == 2, 'compound from svg ' + sp.typename);
    return {msg: 'bezier handles set; SVG "M…Z M…Z" -> compound path with a hole', px: [[500, 120, RED, 15], [500, 145, WHITE, 15]]}; }},
  // ── colors
  {cat: 'color', name: 'hex / CMYK / gray / spot / swatch', fn: function () {
    var a = AI.rect(0, 0, 50, 50, {fill: '#1e90ff'}), g = AI.rect(60, 0, 50, 50, {fill: {gray: 50}}), s = AI.rect(120, 0, 50, 50, {fill: {spot: 'Brand Red', color: {c: 0, m: 95, y: 90, k: 0}, tint: 60}});
    AI.swatch('brand blue', '#1e90ff');
    A(AI.toRGB(a.fillColor).join() == '30,144,255', 'hex ' + AI.toRGB(a.fillColor)); A(g.fillColor.typename == 'GrayColor' && near(g.fillColor.gray, 50), 'gray');
    A(s.fillColor.typename == 'SpotColor' && s.fillColor.spot.name == 'Brand Red' && near(s.fillColor.tint, 60), 'spot');
    A(AI.D().swatches.getByName('brand blue').color.typename == 'RGBColor', 'swatch');
    return 'hex #1e90ff -> 30,144,255; gray 50%; spot "Brand Red" tint 60; swatch "brand blue"'; }},
  {cat: 'color', name: 'linear + radial gradient fills', fn: function () {
    var r = AI.rect(0, 0, 400, 200, {fill: AI.gradient([[0, RED], [1, BLUE]], {angle: 0}), stroke: null});
    var e = AI.ellipse(450, 0, 200, 200, {fill: AI.gradient([[0, WHITE], [0.5, GREEN, 100, 30], [1, [0, 0, 0]]], {type: 'radial'}), stroke: null});
    var g = r.fillColor.gradient; A(g.gradientStops.length == 2 && g.type == GradientType.LINEAR, 'linear'); A(e.fillColor.gradient.gradientStops.length == 3 && e.fillColor.gradient.type == GradientType.RADIAL, 'radial');
    A(near(e.fillColor.gradient.gradientStops[1].midPoint, 30, 1), 'midpoint');
    return {msg: 'linear 2 stops (red→blue), radial 3 stops with midpoint 30', px: [[10, 100, RED, 40], [390, 100, BLUE, 40], [550, 100, WHITE, 30]]}; }},
  // ── style
  {cat: 'style', name: 'opacity / blend mode / layer / name', fn: function () {
    AI.rect(0, 0, 300, 300, {fill: BLUE, stroke: null}); var r = AI.rect(100, 100, 300, 300, {fill: RED, stroke: null, opacity: 50, blend: 'multiply', name: 'top', layer: 'FX'});
    A(near(r.opacity, 50) && r.blendingMode == BlendModes.MULTIPLY && r.name == 'top' && r.layer.name == 'FX', 'style');
    return {msg: '50% multiply on layer "FX"', px: [[200, 200, [28, 33, 123], 15]]}; }},
  // ── layout
  {cat: 'layout', name: 'moveTo / scaleTo (keep aspect) / rotate / flip', fn: function () {
    var r = AI.rect(0, 0, 100, 50, {fill: RED}); AI.moveTo(r, 300, 200); A(Bx(r).join() == '300,200,100,50', 'move ' + Bx(r));
    AI.scaleTo(r, 200, 200, true); A(near(AI.box(r).w, 200) && near(AI.box(r).h, 100), 'scale ' + Bx(r));
    var t = AI.rect(0, 0, 100, 20, {fill: BLUE}); AI.rotate(t, 90); A(near(AI.box(t).w, 20) && near(AI.box(t).h, 100), 'rotate ' + Bx(t));
    var f = AI.path([[0, 0], [100, 0], [0, 50]], {fill: GREEN}); AI.flip(f, 'h'); A(AI.xy(f.pathPoints[0].anchor)[0] > 50, 'flip');
    return 'move to 300,200; fit 200x200 keep aspect -> 200x100; rotate 90 swaps w/h; flip mirrors anchors'; }},
  {cat: 'layout', name: 'align to artboard and to selection', fn: function () {
    var a = AI.rect(10, 10, 100, 100, {fill: RED}), b = AI.rect(300, 200, 50, 80, {fill: BLUE});
    AI.align([a, b], 'hcenter', 'artboard'); A(near(AI.box(a).x, 350) && near(AI.box(b).x, 375), 'hcenter ' + Bx(a) + ' ' + Bx(b));
    AI.align([a, b], 'bottom'); A(near(AI.box(a).y + 100, AI.box(b).y + 80), 'bottom');
    AI.align([a, b], 'top', a); A(near(AI.box(b).y, AI.box(a).y), 'key object');
    return 'centered on 800 pt artboard (x 350 / 375); bottoms equal; key-object top align'; }},
  {cat: 'layout', name: 'distribute equal spacing / fixed gap / grid', fn: function () {
    var L = [AI.rect(0, 0, 40, 40), AI.rect(100, 0, 80, 40), AI.rect(500, 0, 40, 40)]; AI.distribute(L, 'h');
    var g1 = AI.box(L[1]).x - 40, g2 = 500 - (AI.box(L[1]).x + 80); A(near(g1, g2), 'gaps ' + g1 + ' ' + g2);
    var M = [AI.rect(0, 100, 30, 30), AI.rect(0, 200, 30, 50), AI.rect(0, 400, 30, 30)]; AI.distribute(M, 'v', {gap: 10});
    A(near(AI.box(M[1]).y, 140) && near(AI.box(M[2]).y, 200), 'fixed gap ' + Bx(M[1]) + Bx(M[2]));
    var G = []; for (var i = 0; i < 6; i++) G.push(AI.rect(0, 0, 50, 50)); AI.grid(G, 3, 10, 20, 100, 300);
    A(Bx(G[4]).join() == '160,370,50,50', 'grid ' + Bx(G[4]));
    return 'equal gaps ' + Math.round(g1) + ' pt; fixed 10 pt gap; 3-column grid'; }},
  // ── structure
  {cat: 'structure', name: 'group / ungroup', fn: function () {
    var a = AI.rect(0, 0, 50, 50), b = AI.rect(60, 0, 50, 50), g = AI.group([a, b], 'pair');
    A(g.typename == 'GroupItem' && g.pageItems.length == 2 && g.name == 'pair', 'group'); var out = AI.ungroup(g); A(out.length == 2 && AI.D().groupItems.length == 0, 'ungroup');
    return 'group of 2 named "pair", ungroup restores 2 items'; }},
  {cat: 'structure', name: 'clipping mask', fn: function () {
    var img = AI.rect(0, 0, 400, 400, {fill: RED, stroke: null}), m = AI.circle(200, 200, 100); var g = AI.clip(m, [img]);
    A(g.clipped && g.pageItems[0].clipping, 'clipped'); return {msg: 'circle clips the square', px: [[200, 200, RED, 10], [20, 20, WHITE, 10]]}; }},
  {cat: 'structure', name: 'compound path (hole)', fn: function () {
    var c = AI.compound([AI.rect(100, 100, 300, 300), AI.rect(200, 200, 100, 100)]); for (var k = 0; k < c.pathItems.length; k++) { c.pathItems[k].filled = true; c.pathItems[k].fillColor = AI.rgb(20, 170, 60); }
    A(c.typename == 'CompoundPathItem' && c.pathItems.length == 2, 'compound');
    return {msg: 'outer 300x300, inner 100x100 hole', px: [[150, 150, GREEN, 20], [250, 250, WHITE, 10]]}; }},
  // ── pathfinder
  {cat: 'pathfinder', name: 'unite / minusFront / intersect / exclude', fn: function () {
    var u = AI.pathfinder([AI.rect(0, 0, 100, 100, {fill: RED}), AI.rect(50, 50, 100, 100, {fill: RED})], 'unite');
    var ub = AI.box(u); A(near(ub.w, 150) && near(ub.h, 150), 'unite ' + Bx(u));
    var m = AI.pathfinder([AI.rect(300, 0, 100, 100, {fill: BLUE}), AI.rect(370, 0, 100, 100, {fill: BLUE})], 'minusFront');
    A(near(AI.box(m).w, 70) && near(AI.box(m).x, 300), 'minus front (back 300-400 minus front 370-470) ' + Bx(m));   // asymmetric: catches a front/back swap
    var i = AI.pathfinder([AI.rect(0, 300, 100, 100, {fill: GREEN}), AI.rect(50, 350, 100, 100, {fill: GREEN})], 'intersect');
    A(near(AI.box(i).w, 50) && near(AI.box(i).h, 50), 'intersect ' + Bx(i));
    var x = AI.pathfinder([AI.rect(300, 300, 100, 100, {fill: RED}), AI.rect(350, 350, 100, 100, {fill: RED})], 'exclude');
    return {msg: 'unite 150x150, minus front keeps the back 70 wide, intersect 50x50, exclude hole', px: [[375, 375, WHITE, 10], [320, 320, RED, 20]]}; }},
  {cat: 'pathfinder', name: 'divide / trim / crop', fn: function () {
    var d = AI.pathfinder([AI.rect(0, 0, 100, 100, {fill: RED}), AI.rect(50, 0, 100, 100, {fill: BLUE})], 'divide');
    var n = d.typename == 'GroupItem' ? d.pageItems.length : 0; A(n == 3, 'divide pieces ' + n);
    var c = AI.pathfinder([AI.rect(300, 0, 200, 200, {fill: RED}), AI.circle(400, 100, 60, {fill: BLUE})], 'crop'); A(c.typename == 'GroupItem', 'crop');
    return 'divide -> 3 pieces; crop keeps the circle area'; }},
  // ── text
  {cat: 'text', name: 'point text: font, size, color, tracking, top-left placement', fn: function () {
    var t = AI.text('Hello Illustrator', 100, 100, {size: 48, color: RED, tracking: 50, font: 'ArialMT'});
    var ca = t.textRange.characterAttributes; A(near(ca.size, 48) && ca.tracking == 50 && AI.toRGB(ca.fillColor).join() == '220,30,30', 'attrs');
    A(near(AI.box(t).y, 100, 1), 'top at y=100: ' + Bx(t)); A(ca.textFont.name == 'ArialMT', 'font ' + ca.textFont.name);
    return {msg: 'Arial 48 pt, tracking 50, top of text box at y 100 (' + Bx(t) + ')', px: []}; }},
  {cat: 'text', name: 'area text: width, alignment, leading', fn: function () {
    var t = AI.text('Area text wraps inside its box. Area text wraps inside its box. Area text wraps.', 50, 50, {width: 300, height: 200, size: 20, leading: 30, align: 'center'});
    A(t.kind == TextType.AREATEXT && t.lines.length > 1, 'wrap ' + t.lines.length); A(t.textRange.paragraphAttributes.justification == Justification.CENTER, 'center');
    A(near(t.textRange.characterAttributes.leading, 30) && !t.textRange.characterAttributes.autoLeading, 'leading');
    return 'area text 300 wide wraps to ' + t.lines.length + ' lines, centered, leading 30'; }},
  {cat: 'text', name: 'mixed styles in one frame (runs)', fn: function () {
    var t = AI.text('x', 50, 100, {size: 30}); AI.runs(t, [{t: 'Big ', size: 60, color: RED}, {t: 'small', size: 20, color: BLUE, underline: true}]);
    var s0 = t.characters[0].characterAttributes.size, s5 = t.characters[5].characterAttributes.size;   // never hold two attribute objects at once: they alias
    var u5 = t.characters[5].characterAttributes.underline, b5 = AI.toRGB(t.characters[5].characterAttributes.fillColor)[2];
    A(t.contents == 'Big small', 'contents'); A(near(s0, 60) && near(s5, 20) && u5 && b5 == 220, 'runs ' + [s0, s5, u5, b5]);
    return '"Big " 60 pt red + "small" 20 pt blue underlined'; }},
  {cat: 'text', name: 'vertical CJK text + OpenType caps', fn: function () {
    var v = AI.text('直排文字測試', 600, 50, {size: 30, vertical: true}); A(v.orientation == TextOrientation.VERTICAL, 'vertical');
    var c = AI.text('small caps', 50, 300, {size: 30, caps: 'small', set: {fractions: true}}); A(c.textRange.characterAttributes.capitalization == FontCapsOption.SMALLCAPS && c.textRange.characterAttributes.fractions, 'caps');
    A(AI.box(v).h > AI.box(v).w, 'taller than wide ' + Bx(v));
    return 'vertical frame ' + Bx(v) + '; SMALLCAPS + fractions'; }},
  {cat: 'text', name: 'text on a path', fn: function () {
    var c = AI.circle(400, 300, 150); var t = AI.textOnPath(c, 'Text running around a circle', {size: 24});
    A(t.kind == TextType.PATHTEXT && t.contents.length > 10, 'path text'); return 'PATHTEXT on a circle'; }},
  {cat: 'text', name: 'fit text to width + create outlines', fn: function () {
    var t = AI.text('A headline that is too long', 50, 50, {size: 80}); AI.fitText(t, 300); A(AI.box(t).w <= 300, 'fit ' + Bx(t));
    var g = AI.outline(t); A(g.typename == 'GroupItem' && AI.D().textFrames.length == 0, 'outlines'); return 'shrunk to ≤300 wide, then outlined -> group of paths'; }},
  {cat: 'text', name: 'character + paragraph styles', fn: function () {
    var cs = AI.charStyle('Accent', {size: 40, color: RED}), ps = AI.paraStyle('Body', {size: 18, align: 'right', spaceAfter: 12});
    var t = AI.text('Styled', 100, 100); cs.applyTo(t.textRange, true);
    A(near(t.textRange.characterAttributes.size, 40), 'char style size'); var t2 = AI.text('Para', 100, 200); ps.applyTo(t2.textRange, true);
    A(t2.textRange.paragraphAttributes.justification == Justification.RIGHT && near(t2.textRange.paragraphAttributes.spaceAfter, 12), 'para style');
    return 'character style "Accent" 40 pt red; paragraph style "Body" right, space after 12'; }},
  // ── effects (read back from the saved .ai)
  {cat: 'effects', name: 'drop shadow + outer glow + round corners', fn: function () {
    var r = AI.rect(100, 100, 200, 150, {fill: RED}); AI.dropShadow(r, {x: 6, y: 6, blur: 4, opacity: 0.6}); AI.roundCorners(r, 20);
    var t = AI.text('Glow', 400, 100, {size: 60}); AI.outerGlow(t, {blur: 10});
    A(r.visibleBounds[2] > r.geometricBounds[2] + 3, 'shadow widens visible bounds'); return {msg: 'shadow widens visible bounds by ' + Math.round(r.visibleBounds[2] - r.geometricBounds[2]) + ' pt', fx: ['Adobe Drop Shadow', 'Adobe Round Corners', 'Adobe Outer Glow']}; }},
  {cat: 'effects', name: 'offset path / feather / gaussian blur / roughen / warp', fn: function () {
    var a = AI.rect(50, 50, 100, 100, {fill: BLUE}); AI.offsetPath(a, 15); A(near(a.visibleBounds[2] - a.geometricBounds[2], 16, 1.5), 'offset ' + (a.visibleBounds[2] - a.geometricBounds[2]));
    AI.feather(AI.rect(200, 50, 100, 100, {fill: GREEN}), 8); AI.gaussianBlur(AI.rect(350, 50, 100, 100, {fill: RED}), 6);
    AI.roughen(AI.rect(500, 50, 100, 100, {fill: BLUE}), 8, 12); AI.warp(AI.text('WARP', 100, 300, {size: 70}), 1, 0.6);
    return {msg: 'offset path grows visible bounds by 15 pt; 5 effects stored', fx: ['Adobe Offset Path', 'Adobe Fuzzy Mask', 'Adobe PSL Gaussian Blur', 'Adobe Roughen', 'Adobe Deform']}; }},
  {cat: 'effects', name: 'expand appearance', fn: function () {
    var r = AI.rect(100, 100, 100, 100, {fill: RED}); AI.offsetPath(r, 20); var e = AI.expandAppearance(r);
    var b = AI.box(e.typename ? e : e[0]); A(near(b.w, 142, 2), 'expanded width ' + b.w); return 'offset baked into geometry: ' + Math.round(b.w) + ' pt wide'; }},
  // ── images / symbols / styles
  {cat: 'image', name: 'place + embed + fit + clip image', fn: function () {
    var png = AI.png(TMP + '/_img_src.png', {scale: 50}); var p = AI.place(png, 100, 100, {w: 200});
    A(p.typename == 'PlacedItem' && near(AI.box(p).w, 200), 'placed ' + Bx(p));
    var e = AI.place(png, 400, 100, {w: 150, embed: true}); A(e.typename == 'RasterItem', 'embedded ' + e.typename);
    var g = AI.clip(AI.circle(475, 170, 50), [e]); A(g.clipped, 'clip');
    return 'placed 200 wide (linked), embedded RasterItem 150 wide, clipped to circle'; }},
  {cat: 'image', name: 'image trace -> vector paths', fn: function () {
    AI.circle(200, 200, 150, {fill: RED, stroke: null}); var png = AI.png(TMP + '/_trace_src.png', {scale: 50});
    AI.D().pageItems.removeAll(); var p = AI.place(png, 0, 0, {embed: true});
    var out = AI.trace(p, null, true); var n = AI.D().pathItems.length; A(n >= 1, 'paths ' + n);
    return 'traced raster -> ' + n + ' paths'; }},
  {cat: 'image', name: 'rasterize vector art', fn: function () {
    var r = AI.rasterize(AI.star(200, 200, 100, 40, 5, {fill: GREEN}), {resolution: 72}); A(r.typename == 'RasterItem', r.typename);
    return {msg: 'star -> RasterItem', px: [[200, 200, GREEN, 30]]}; }},
  {cat: 'symbols', name: 'symbol create + place instances', fn: function () {
    var s = AI.symbol(AI.star(0, 0, 30, 12, 5, {fill: RED}), 'StarSym'); var a = AI.placeSymbol('StarSym', 100, 100), b = AI.placeSymbol(s, 300, 100);
    A(a.symbol.name == 'StarSym' && AI.D().symbolItems.length >= 2 && near(AI.box(b).x, 300), 'symbols');
    return 'symbol "StarSym" with 2 instances'; }},
  {cat: 'symbols', name: 'graphic style applied', fn: function () {
    var D = AI.D(), n = D.graphicStyles.length; A(n > 1, 'document has ' + n + ' graphic styles');
    var r = AI.rect(100, 100, 100, 100); var gs = D.graphicStyles[1]; gs.applyTo(r); return 'applied "' + gs.name + '" (' + n + ' styles available)'; }},
  {cat: 'structure', name: 'repeat radial / grid / mirror', fn: function () {
    var a = AI.repeat(AI.circle(200, 150, 20, {fill: RED}), 'radial'), b = AI.repeat(AI.rect(500, 50, 30, 30, {fill: BLUE}), 'grid'), c = AI.repeat(AI.rect(100, 400, 30, 30, {fill: GREEN}), 'mirror');
    A(a.typename == 'RadialRepeatItem' && b.typename == 'GridRepeatItem' && c.typename == 'SymmetryRepeatItem', [a.typename, b.typename, c.typename].join());
    return 'RadialRepeatItem, GridRepeatItem, SymmetryRepeatItem'; }},
  {cat: 'structure', name: 'blend two shapes', fn: function () {
    var n0 = AI.D().pluginItems.length; var b = AI.blend([AI.circle(100, 300, 30, {fill: RED}), AI.circle(700, 300, 30, {fill: BLUE})]);
    A(b && b.typename == 'PluginItem' && AI.D().pluginItems.length > n0, 'blend ' + (b && b.typename)); return 'blend object (PluginItem)'; }},
  // ── document
  {cat: 'document', name: 'newDoc with safe-zone guides + background', fn: function () {
    var base = AI.D(), D = AI.newDoc(1080, 1920, '_preset_test', {safe: [65, 269, 65, 672], bg: [244, 242, 238]});
    var ab = AI.ab(0), gl = D.layers.getByName('Guides'), g = [];
    for (var i = 0; i < gl.pathItems.length; i++) { var it = gl.pathItems[i], p = AI.xy(it.pathPoints[0].anchor); g.push(Math.abs(it.pathPoints[0].anchor[0] - it.pathPoints[1].anchor[0]) < 0.01 ? 'V' + Math.round(p[0]) : 'H' + Math.round(p[1])); }
    var bg = D.layers.getByName('Background'), ok = near(ab.w, 1080) && near(ab.h, 1920) && bg.locked && bg.pathItems.length == 1 && AI.toRGB(bg.pathItems[0].fillColor).join() == '244,242,238';
    D.close(SaveOptions.DONOTSAVECHANGES); base.activate();
    A(ok, 'size/background'); A(g.sort().join() == ['H1248', 'H269', 'V1015', 'V65'].sort().join(), 'guides ' + g.join());
    return '1080×1920, guides ' + g.join(' ') + ', locked background'; }},
  {cat: 'document', name: 'multiple artboards + add + fit to art', fn: function () {
    var base = AI.D(), D = AI.newDoc(400, 300, '_ab_test', {artboards: 3, spacing: 50}); A(D.artboards.length == 3, 'n ' + D.artboards.length);
    AI.addArtboard(0, 500, 200, 200, 'extra'); A(D.artboards.length == 4 && D.artboards[3].name == 'extra', 'add');
    D.artboards.setActiveArtboardIndex(3); var r = AI.rect(20, 20, 50, 60, {stroke: null}); AI.fitArtboard(3, [r]); var a = AI.ab(3);
    var ok = near(a.w, 50) && near(a.h, 60); D.close(SaveOptions.DONOTSAVECHANGES); base.activate(); A(ok, 'fit ' + a.w + 'x' + a.h);
    return '3 artboards + "extra"; fit artboard to selected art = 50x60'; }},
  {cat: 'document', name: 'layers: create, lock, hide, order', fn: function () {
    var L = AI.layer('Top', {locked: false}), M = AI.layer('Hidden', {visible: false}); A(!M.visible && AI.D().layers.length >= 3, 'layers');
    L.zOrder(ZOrderMethod.BRINGTOFRONT); A(AI.D().layers[0].name == 'Top', 'order ' + AI.D().layers[0].name); return 'layer "Top" in front, "Hidden" invisible'; }},
  // ── export (files read back)
  {cat: 'export', name: 'PNG / JPG / WebP / SVG / PDF / PSD', fn: function () {
    AI.rect(100, 100, 300, 200, {fill: RED}); AI.text('Export', 150, 150, {size: 40});
    var f = [AI.png(TMP + '/_e.png', {scale: 50}).fsName, AI.png(TMP + '/_e2x.png', {scale: 200, transparent: true}).fsName, AI.jpg(TMP + '/_e.jpg', {quality: 70}).fsName,
      AI.webp(TMP + '/_e.webp', {quality: 80}).fsName, AI.svg(TMP + '/_e.svg', {outlineText: true}).fsName, AI.psd(TMP + '/_e.psd').fsName];
    return {msg: 'png 50% / 200% transparent, jpg, webp, svg (outlined text), psd', files: f, size: {png: [400, 300], png2: [1600, 1200]}}; }},
  {cat: 'export', name: 'export for screens (all artboards x 2 formats)', fn: function () {
    var base = AI.D(), D = AI.newDoc(200, 100, '_efs', {artboards: 2}); AI.rect(10, 10, 50, 50, {fill: RED});
    var dir = TMP + '/_efs'; var F = new Folder(dir); if (F.exists) { var old = F.getFiles(); for (var i = 0; i < old.length; i++) try { old[i].remove(); } catch (e) {} }
    AI.exportScreens(dir, {formats: ['png', 'svg'], scale: 2}); D.close(SaveOptions.DONOTSAVECHANGES); base.activate();
    var got = []; function walk(f) { var L = f.getFiles(); for (var i = 0; i < L.length; i++) { if (L[i] instanceof Folder) walk(L[i]); else got.push(L[i].fsName); } } walk(new Folder(dir));
    A(got.length >= 4, 'files ' + got.length); return {msg: got.length + ' files (2 artboards × png@2x + svg)', files: got}; }},
  {cat: 'export', name: 'PDF save + reopen', fn: function () {
    var base = AI.D(), D = AI.newDoc(300, 200, '_pdf', {artboards: 2}); AI.rect(10, 10, 100, 100, {fill: BLUE}); var f = AI.pdf(TMP + '/_e.pdf', {preset: '[High Quality Print]'});
    D.close(SaveOptions.DONOTSAVECHANGES); base.activate();
    f.encoding = 'BINARY'; f.open('r'); var raw = f.read(); f.close(); var pages = (raw.match(/\/Type\s*\/Page[^s]/g) || []).length;
    var R = app.open(f); var ok = R.pageItems.length >= 1; R.close(SaveOptions.DONOTSAVECHANGES); base.activate();
    A(pages == 2 && ok, 'pages ' + pages); return {msg: 'PDF [High Quality Print]: 2 pages in the file, reopens in Illustrator', files: [f.fsName]}; }}
];

function listTests() { var o = []; for (var i = 0; i < TESTS.length; i++) o.push({i: i, cat: TESTS[i].cat, name: TESTS[i].name}); return o; }
function runOne(i) {
  var t = TESTS[i], t0 = new Date().getTime(), base = null, r;
  try {
    CLOSEALL(); NEWDOC(800, 600, '_t' + i); app.activeDocument.artboards.setActiveArtboardIndex(0);
    var v = t.fn(); r = typeof v == 'string' ? {msg: v} : v; r.ok = true;
  } catch (e) { r = {ok: false, msg: String(e) + (e.line ? ' (line ' + e.line + ')' : '')}; }
  r.ms = new Date().getTime() - t0; r.cat = t.cat; r.name = t.name;
  return r;
}
TESTS.push({cat: 'text', name: 'fit headline (tracking fills one line)', fn: function () {
  var t = AI.text('HEADLINE', 50, 50, {width: 400, height: 80, size: 30}); AI.fitHeadline(t);
  var tr = t.textRange.characterAttributes.tracking; A(tr > 100 && t.lines.length == 1, 'tracking ' + tr + ' lines ' + t.lines.length);
  return 'tracking ' + tr + ' keeps "HEADLINE" on one 400 pt line'; }});
TESTS.push({cat: 'text', name: 'thread two area-text frames', fn: function () {
  var a = AI.text('One two three four five six seven eight nine ten eleven twelve thirteen fourteen', 50, 50, {width: 120, height: 40, size: 14});
  var b = AI.text('', 50, 200, {width: 120, height: 120, size: 14}); AI.thread(a, b);
  A(a.nextFrame && b.previousFrame && b.lines.length > 0, 'threaded'); return 'text flows from frame 1 into frame 2 (' + b.lines.length + ' lines there)'; }});

// Document fingerprint: hash each part of the active document so a command can be checked for a *real* effect.
// FP() -> {items, text, layers, boards, swatches, symbols, styles, brushes, doc, sel, n}   (each value a short hash)
// FPDIFF(a, b) -> names of the parts that changed.  FPRAW(part) -> the full serialized string (debugging).
// Appearance that the DOM cannot see (live effects, brushes applied, 3D...) is covered by the Python side
// (tests/fp.py: 'art' = hash of an uncompressed .ai save, 'pix' = hash of a PNG export).
function __h(s) {                                    // 32-bit FNV-1a, hex
  var h = 0x811c9dc5;
  for (var i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = (h + ((h << 1) + (h << 4) + (h << 7) + (h << 8) + (h << 24))) >>> 0; }
  return ('0000000' + h.toString(16)).slice(-8) + ':' + s.length;
}
function __r(v) { return Math.round(v * 100) / 100; }
function __b(b) { try { return [__r(b[0]), __r(b[1]), __r(b[2]), __r(b[3])].join(','); } catch (e) { return '?'; } }
function __col(c) {
  if (!c) return 'null';
  try {
    switch (c.typename) {
      case 'RGBColor': return 'rgb(' + __r(c.red) + ',' + __r(c.green) + ',' + __r(c.blue) + ')';
      case 'CMYKColor': return 'cmyk(' + __r(c.cyan) + ',' + __r(c.magenta) + ',' + __r(c.yellow) + ',' + __r(c.black) + ')';
      case 'GrayColor': return 'gray(' + __r(c.gray) + ')';
      case 'LabColor': return 'lab(' + __r(c.l) + ',' + __r(c.a) + ',' + __r(c.b) + ')';
      case 'NoColor': return 'none';
      case 'SpotColor': return 'spot(' + c.spot.name + ',' + __r(c.tint) + ',' + __col(c.spot.color) + ')';
      case 'PatternColor': return 'pattern(' + c.pattern.name + ',' + __r(c.rotation) + ',' + __r(c.scaleFactor[0]) + ')';
      case 'GradientColor':
        var g = c.gradient, st = [];
        for (var i = 0; i < g.gradientStops.length; i++) { var s = g.gradientStops[i]; st.push(__r(s.rampPoint) + '/' + __r(s.midPoint) + '/' + __r(s.opacity) + '/' + __col(s.color)); }
        return 'grad(' + g.type + ',' + __r(c.angle) + ',' + st.join(';') + ')';
    }
  } catch (e) {}
  return c.typename;
}
function __try(f) { try { return f(); } catch (e) { return '!'; } }
function __item(it) {
  var s = [it.typename, __try(function () { return it.name; }), __b(it.geometricBounds), __try(function () { return __b(it.visibleBounds); }),
    it.hidden, it.locked, __try(function () { return __r(it.opacity); }), __try(function () { return it.blendingMode; }),
    __try(function () { return it.isIsolated; }), __try(function () { return it.artworkKnockout; }), __try(function () { return it.note; }),
    __try(function () { return it.wrapped + '/' + it.wrapOffset + '/' + it.wrapInside; })];
  var t = it.typename;
  if (t == 'PathItem') {
    s.push(it.closed, it.clipping, it.guides, it.evenodd, it.filled, __col(it.fillColor), it.fillOverprint, it.stroked, __col(it.strokeColor),
      __r(it.strokeWidth), it.strokeCap, it.strokeJoin, __r(it.strokeMiterLimit), String(it.strokeDashes), it.strokeOverprint, it.polarity, it.pixelAligned);
    var P = it.pathPoints, pts = [];
    for (var i = 0; i < P.length; i++) { var p = P[i]; pts.push(__r(p.anchor[0]) + ' ' + __r(p.anchor[1]) + ' ' + __r(p.leftDirection[0]) + ' ' + __r(p.leftDirection[1]) + ' ' + __r(p.rightDirection[0]) + ' ' + __r(p.rightDirection[1]) + ' ' + p.pointType); }
    s.push(pts.join('|'));
  } else if (t == 'CompoundPathItem') {
    s.push(it.pathItems.length);
  } else if (t == 'GroupItem') {
    s.push(it.clipped, it.pageItems.length);
  } else if (t == 'TextFrame') {
    s.push(it.kind, it.contents, it.orientation, __try(function () { return __b(it.textPath.geometricBounds); }), it.columnCount, it.rowCount, it.opticalAlignment, __try(function () { return it.antialias; }));
  } else if (t == 'PlacedItem') {
    s.push(__try(function () { return decodeURI(it.file.name); }), __try(function () { var m = it.matrix; return [m.mValueA, m.mValueB, m.mValueC, m.mValueD].join(','); }));
  } else if (t == 'RasterItem') {
    s.push(it.embedded, it.imageColorSpace, it.bitsPerChannel, it.channels, __try(function () { var m = it.matrix; return [__r(m.mValueA), __r(m.mValueB), __r(m.mValueC), __r(m.mValueD)].join(','); }));
  } else if (t == 'SymbolItem') {
    s.push(it.symbol.name);
  } else if (t == 'PluginItem') {
    s.push(it.isTracing);
  } else if (t == 'GraphItem' || t == 'MeshItem' || t == 'LegacyTextItem' || t == 'NonNativeItem') {
    // bounds already cover them
  }
  return s.join('~');
}
function __text(D) {
  var out = [];
  for (var i = 0; i < D.textFrames.length; i++) {
    var tf = D.textFrames[i], R = tf.textRange, cs = [];
    for (var j = 0; j < R.characters.length && j < 400; j++) {
      var ch = R.characters[j], a = ch.characterAttributes;
      cs.push(__try(function () { return [a.textFont.name, __r(a.size), __r(a.tracking), __r(a.leading), a.autoLeading, __r(a.horizontalScale), __r(a.verticalScale), __r(a.baselineShift), __r(a.rotation),
        a.capitalization, a.baselinePosition, a.underline, a.strikeThrough, a.ligature, a.discretionaryLigature, a.contextualLigature, a.fractions, a.ordinals, a.swash,
        a.titling, a.stylisticAlternates, a.figureStyle, a.openTypePosition, a.kerningMethod, a.language, a.noBreak, a.fillColor ? __col(a.fillColor) : '-', a.strokeColor ? __col(a.strokeColor) : '-',
        __r(a.strokeWeight), a.overprintFill, a.alternateGlyphs, a.tateChuYokoHorizontal, a.Tsume, a.wariChuEnabled].join('/'); }));
    }
    var ps = [];
    for (j = 0; j < R.paragraphs.length && j < 50; j++) {
      var pa = R.paragraphs[j].paragraphAttributes;
      ps.push(__try(function () { return [pa.justification, __r(pa.firstLineIndent), __r(pa.leftIndent), __r(pa.rightIndent), __r(pa.spaceBefore), __r(pa.spaceAfter), pa.hyphenation, pa.everyLineComposer, pa.kinsoku, pa.mojikumi, pa.romanHanging, pa.bunriKinshi, pa.burasagariType, pa.kurikaeshiMojiShori, pa.autoLeadingAmount, pa.leadingType, pa.singleWordJustification, pa.desiredWordSpacing, pa.desiredLetterSpacing, pa.desiredGlyphScaling, (pa.tabStops || []).length].join('/'); }));
    }
    out.push(tf.contents + '#' + cs.join(',') + '#' + ps.join(','));
  }
  return out.join('\n');
}
function __coll(C, f) { var a = []; try { for (var i = 0; i < C.length; i++) a.push(f ? f(C[i]) : C[i].name); } catch (e) { a.push('!'); } return a.join('|'); }
function __layers(C, depth) {
  return __coll(C, function (L) {
    return [L.name, L.visible, L.locked, L.printable, L.preview, L.dimPlacedImages, __r(L.opacity), L.blendingMode, L.isIsolated, L.hasSelectedArtwork, L.sliced,
      __try(function () { return __col(L.color); }), L.pageItems.length, depth < 4 ? '[' + __layers(L.layers, depth + 1) + ']' : ''].join('/');
  });
}
function FPRAW(part, D) {
  D = D || app.activeDocument;
  switch (part) {
    case 'items': return __coll(D.pageItems, __item);
    case 'text': return __text(D);
    case 'layers': return __layers(D.layers, 0);
    case 'boards': return __coll(D.artboards, function (a) { return a.name + ':' + __b(a.artboardRect) + ':' + __try(function () { return a.rulerOrigin + '/' + a.showCenter + '/' + a.showCrossHairs; }); }) + '#' + D.artboards.getActiveArtboardIndex();
    case 'swatches': return __coll(D.swatches, function (s) { return s.name + '=' + __col(s.color); }) + '#' + __coll(D.swatchGroups) + '#' + __coll(D.gradients) + '#' + __coll(D.patterns) + '#' + __coll(D.spots, function (s) { return s.name + '=' + s.colorType + __col(s.color); });
    case 'symbols': return __coll(D.symbols) + '#' + D.symbolItems.length;
    case 'styles': return __coll(D.graphicStyles) + '#' + __coll(D.characterStyles) + '#' + __coll(D.paragraphStyles) + '#' + __try(function () { return __coll(D.listStyles); });
    case 'brushes': return __coll(D.brushes) + '#' + __coll(D.variables, function (v) { return v.name + '/' + v.kind; }) + '#' + __coll(D.dataSets) + '#' + __coll(D.tags, function (t) { return t.name + '=' + t.value; });
    case 'doc': return [D.documentColorSpace, __try(function () { return D.rulerOrigin.join(','); }), D.rulerUnits, __try(function () { return D.pageOrigin.join(','); }),
      __try(function () { var r = D.rasterEffectSettings; return [r.resolution, r.colorModel, r.antiAliasing, r.clippingMask, r.padding, r.transparency].join('/'); }),
      __try(function () { return D.XMPString.replace(/<xmp:(ModifyDate|MetadataDate|CreateDate)>[^<]*</g, '').replace(/(uuid|xmp\.[id]id):[0-9a-f-]+/g, '').replace(/<stEvt:when>[^<]*</g, '').length; }),
      D.stationery, D.showPlacedImages, D.splitLongPaths, D.useDefaultScreen, __try(function () { return D.cropBox.join(','); }), D.cropStyle,
      __try(function () { return D.isGridVisible() + '/' + D.isGuideVisible() + '/' + D.isRulerVisible() + '/' + D.isTransparencyGridVisible(); }),
      __try(function () { return D.kinsokuSet + '/' + D.mojikumiSet; }), __try(function () { return D.defaultFilled + __col(D.defaultFillColor) + D.defaultStroked + __col(D.defaultStrokeColor) + D.defaultStrokeWidth; }),
      __try(function () { return D.inkList.length; })].join('~');
    case 'sel': var S = D.selection; if (!S) return 'null'; if (S.typename == 'TextRange') return 'text:' + S.contents; return __coll(S, function (x) { return x.typename + ':' + __b(x.geometricBounds); });
  }
  return '';
}
var FP_PARTS = ['items', 'text', 'layers', 'boards', 'swatches', 'symbols', 'styles', 'brushes', 'doc', 'sel'];
function FP(D) {
  D = D || app.activeDocument; var f = {};
  for (var i = 0; i < FP_PARTS.length; i++) f[FP_PARTS[i]] = __h(FPRAW(FP_PARTS[i], D));
  f.n = D.pageItems.length;
  return f;
}
function FPDIFF(a, b) { var o = []; for (var k in a) if (String(a[k]) !== String(b[k])) o.push(k); return o; }

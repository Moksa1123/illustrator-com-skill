"""Menu command cases for tests/menu_sweep.py. One entry per menu command (index/menu-index.json).

C(cmd, kind, check, how, act=None, dlg="enter", clip=False)
  kind  sandbox scenario (tests/menu_sweep.jsx SETUP), e.g. "sel2", "txt", "img+saved"
  act   JavaScript to run; default runs the menu command itself: MENU('<cmd>')
        (__N0 / __P0 / __G0 = pageItems / pathItems / groupItems before the action are available)
  check JavaScript expression that must be true afterwards (READ BACK). None = document fingerprint must change
        "deep:a,b" = the art hash of TMP/_d_a.ai and TMP/_d_b.ai (saved inside act with DEEP('a')) must differ
  how   the way to do it from a script (goes into CAPABILITIES.md)
  dlg   what to do with dialogs: "enter" accept defaults, "esc", or a plan list for the first dialog:
        ["sel", "type:30", "tab", "ok"]  ({TMPW} is replaced with the Windows path of the sandbox folder)
  clip  uses the system clipboard (the runner saves and restores its text)
"""
CASES = []


def C(cmd, kind="", check=None, how=None, act=None, dlg="enter", clip=False):
    CASES.append({"cmd": cmd, "kind": kind, "check": check, "how": how or f"app.executeMenuCommand('{cmd}')", "act": act, "dlg": dlg, "clip": clip})


M = lambda c: f"MENU({c!r});"  # noqa: E731

# ── File ──────────────────────────────────────────────────────────────────────
C("new", "none", "__ok", "app.documents.add(DocumentColorSpace.RGB, w, h) / AI.newDoc()",
  act="var n0 = app.documents.length; var nd = app.documents.add(DocumentColorSpace.RGB, 300, 200); var __ok = app.documents.length == n0 + 1 && Math.round(nd.width) == 300; nd.close(SaveOptions.DONOTSAVECHANGES); D.activate();")
C("saveasTemplate", "saved", "new File(TMP + '/_tpl.ait').exists", "File > Save as Template: menu + save dialog (path typed)",
  act="var tf = new File(TMP + '/_tpl.ait'); if (tf.exists) tf.remove(); MENU('saveasTemplate');", dlg=["edit:0:{TMPW}\\_tpl.ait", "wait:0.3", "ok", "wait:1"])
C("newFromTemplate", "none", "__ok", "File > New from Template: menu + open dialog (path typed) -> new untitled document",
  act="var tf = new File(TMP + '/_tpl2.ait'); if (!tf.exists) { var o = new IllustratorSaveOptions(); D.saveAs(tf, o); } var n0 = app.documents.length; MENU('newFromTemplate'); var __ok = app.documents.length == n0 + 1 && app.activeDocument.name.indexOf('_tpl2') < 0;",
  dlg=["edit:0:{TMPW}\\_tpl2.ait", "wait:0.3", "ok"])
C("open", "none", "__ok", "app.open(file)",
  act="var f = new File(TMP + '/_open_src.ai'); SAVEAI(f.fsName); D.close(SaveOptions.DONOTSAVECHANGES); var d2 = app.open(f); var __ok = d2.pageItems.length >= 3;")
C("close", "none", "__ok", "document.close(SaveOptions.DONOTSAVECHANGES)",
  act="NEWDOC(200, 200, 'extra'); var n0 = app.documents.length; app.activeDocument.close(SaveOptions.DONOTSAVECHANGES); var __ok = app.documents.length == n0 - 1;")
C("closeAll", "none", "__ok", "while (documents.length) documents[0].close(DONOTSAVECHANGES)",
  act="NEWDOC(200, 200, 'extra'); var n0 = app.documents.length; CLOSEALL(); var __ok = n0 == 2 && app.documents.length == 0; NEWDOC(100, 100, 'after');")
C("save", "saved", "__ok", "document.save() (or MENU('save') on a saved document)",
  act="var f = new File(TMP + '/_sweep_saved.ai'), t0 = f.modified.getTime(); $.sleep(1200); AI.rect(0, 0, 10, 10); app.activeDocument.save(); var __ok = new File(f.fsName).modified.getTime() > t0 && app.activeDocument.saved;")
C("saveas", "", "__ok", "AI.saveAI(path) = document.saveAs(file, IllustratorSaveOptions)",
  act="var f = new File(TMP + '/_saveas.ai'); if (f.exists) f.remove(); AI.saveAI(f.fsName); var __ok = f.exists && app.activeDocument.name == '_saveas.ai';")
C("saveacopy", "saved", "__ok", "File > Save a Copy: menu + save dialog (path typed); the open document keeps its name",
  act="var cf = new File(TMP + '/_copy.ai'); if (cf.exists) cf.remove(); MENU('saveacopy'); var __ok = new File(TMP + '/_copy.ai').exists && app.activeDocument.name == '_sweep_saved.ai';",
  dlg=["edit:0:{TMPW}\\_copy.ai", "wait:0.3", "ok", "wait:1"])
C("Adobe AI Save Selected Slices", "saved", "__ok", "Save Selected Slices: menu + Save Optimized dialog (path typed)",
  act="MENU('AISlice Make Slice'); AI.select([R]); var imf = new Folder(TMP + '/images'); var n0 = imf.exists ? imf.getFiles().length : 0; MENU('Adobe AI Save Selected Slices'); var __ok = new Folder(TMP + '/images').exists && new Folder(TMP + '/images').getFiles().length > n0 || new File(TMP + '/_slice.png').exists;",
  dlg=["edit:0:{TMPW}\\_slice.png", "wait:0.3", "ok", "wait:1"])
C("revert", "saved", "N('RV') == null && N('R') != null", "File > Revert (confirm dialog accepted)",
  act="AI.rect(0, 0, 10, 10, {name: 'RV'}); MENU('revert');")
C("AI Place", "", "D.placedItems.length == 1 && D.placedItems[0].file.exists", "document.placedItems.add(); item.file = File / AI.place(file, x, y, {w, embed})",
  act="var p = D.placedItems.add(); p.file = IMGFILE();")
C("exportForScreens", "", "__ok", "document.exportForScreens(folder, ExportForScreensType, options, itemToExport) / AI.exportScreens()",
  act="var F = new Folder(TMP + '/_efs_sweep'); if (F.exists) { var L = F.getFiles(); for (var i = 0; i < L.length; i++) try { L[i].remove(); } catch (e) {} } AI.exportScreens(F.fsName, {formats: ['png']}); var cnt = 0; function w(f) { var L = f.getFiles(); for (var i = 0; i < L.length; i++) { if (L[i] instanceof Folder) w(L[i]); else cnt++; } } w(F); var __ok = cnt >= 1;")
C("export", "", "__ok", "document.exportFile(file, ExportType.*, options) / AI.png() AI.jpg() AI.svg() AI.webp() AI.psd()",
  act="var f = new File(TMP + '/_export.png'); if (f.exists) f.remove(); AI.png(f.fsName); var __ok = f.exists && f.length > 100;")
C("Adobe AI Save For Web", "", "__ok", "exportFile(ExportType.GIF / PNG8 / JPEG) (the legacy Save for Web formats)",
  act="var f = new File(TMP + '/_web.gif'); if (f.exists) f.remove(); var o = new ExportOptionsGIF(); o.artBoardClipping = true; D.exportFile(f, ExportType.GIF, o); var __ok = f.exists && f.length > 100;")
C("exportSelection", "", "__ok", "document.exportSelectionAsPNG(path) (Export Selection)",
  act="var f = new File(TMP + '/_expsel.png'); if (f.exists) f.remove(); D.exportSelectionAsPNG(f); var __ok = f.exists && f.length > 100;")
C("Package Menu Item", "saved", "__ok", "File > Package: menu + package dialog (default location next to the .ai)",
  act="function nf() { var n = 0, L = new Folder(TMP).getFiles(); for (var i = 0; i < L.length; i++) if (L[i] instanceof Folder && L[i].name.indexOf('_sweep_saved') >= 0) n++; return n; } var p0 = nf(); MENU('Package Menu Item'); var __ok = nf() > p0;")
C("ai_browse_for_script", "", "N('fromScript') != null", "$.evalFile(file) (File > Scripts > Other Script runs a .jsx the same way)",
  act="var f = new File(TMP + '/_s.jsx'); f.encoding = 'UTF-8'; f.open('w'); f.write(\"var x = app.activeDocument.pathItems.rectangle(10, 10, 5, 5); x.name = 'fromScript';\"); f.close(); $.evalFile(f);")
C("document", "", "deep:a,b", "File > Document Setup: bleed / units / transparency grid are dialog-only; scripting sets them at creation (DocumentPreset) — here the dialog's first field (bleed top) is typed",
  act="DEEP('a'); MENU('document'); DEEP('b');", dlg=["sel", "type:9", "tab", "ok"])
C("doc-color-cmyk", "", "D.documentColorSpace == DocumentColorSpace.CMYK")
C("doc-color-rgb", "cmyk", "D.documentColorSpace == DocumentColorSpace.RGB")
C("File Info", "", "D.XMPString.indexOf('SweepTitle') >= 0", "document.XMPString (File Info edits the XMP metadata)",
  act="D.XMPString = D.XMPString.replace('<dc:format>', '<dc:description><rdf:Alt><rdf:li xml:lang=\"x-default\">SweepTitle</rdf:li></rdf:Alt></dc:description><dc:format>');")
C("Print", "", "__ok", "document.print(PrintOptions) to a PostScript file (printerName = the 'Adobe PostScript File' virtual printer, jobOptions.file)",
  act="var pn = ''; for (var i = 0; i < app.printerList.length; i++) if (/PostScript/i.test(app.printerList[i].name)) pn = app.printerList[i].name; var f = new File(TMP + '/_print.ps'); if (f.exists) f.remove(); var o = new PrintOptions(); var j = new PrintJobOptions(); j.file = f; o.jobOptions = j; if (pn) o.printerName = pn; D.print(o); var __ok = f.exists && f.length > 1000;")
# ── Edit ──────────────────────────────────────────────────────────────────────
C("undo", "", "D.pageItems.length == n1 - 1", "app.undo() / MENU('undo') (undoes the last step of the running script)",
  act="AI.rect(0, 0, 10, 10); app.redraw(); var n1 = D.pageItems.length; app.undo();")
C("redo", "", "D.pageItems.length == n1", "app.redo() / MENU('redo')",
  act="AI.rect(0, 0, 10, 10); app.redraw(); var n1 = D.pageItems.length; app.undo(); app.redo();")
C("cut", "", "D.pageItems.length == __N0 - 1", clip=True)
C("copy", "", "D.pageItems.length == __N0 + 1", "MENU('copy') then MENU('paste')", act="MENU('copy'); MENU('paste');", clip=True)
C("paste", "", "D.pageItems.length == __N0 + 1", act="MENU('copy'); MENU('paste');", clip=True)
C("pasteFront", "", "D.pageItems.length == __N0 + 1 && D.selection[0].absoluteZOrderPosition > R.absoluteZOrderPosition && D.selection[0].geometricBounds.join() == R.geometricBounds.join()",
  act="MENU('copy'); MENU('pasteFront');", clip=True)
C("pasteBack", "", "D.pageItems.length == __N0 + 1 && D.selection[0].absoluteZOrderPosition < R.absoluteZOrderPosition", act="MENU('copy'); MENU('pasteBack');", clip=True)
C("pasteInPlace", "", "D.pageItems.length == __N0 + 1 && D.selection[0].geometricBounds.join() == R.geometricBounds.join()", act="MENU('copy'); MENU('pasteInPlace');", clip=True)
C("pasteInAllArtboard", "", "D.pageItems.length == __N0 + 2", act="AI.addArtboard(0, 700, 800, 600); AI.select([R]); MENU('copy'); MENU('pasteInAllArtboard');", clip=True)
C("pasteWithoutFormatting", "", "__ok", "copy text, place the cursor, MENU('pasteWithoutFormatting')",
  act="T.textRange.characterAttributes.size = 50; T.textRange.select(); MENU('copy'); var T2 = AI.text('x', 100, 500, {size: 12}); T2.textRange.characters[0].select(); MENU('pasteWithoutFormatting'); var __ok = T2.contents.length > 5 && T2.characters[3].characterAttributes.size < 20;", clip=True)
C("clear", "", "D.pageItems.length == __N0 - 1")
C("Find and Replace", "", "T.contents == 'Sample text XYZ' && T.characters[0].characterAttributes.size == 36", "AI.replaceText(find, replace) (keeps character styles)",
  act="AI.replaceText('abc', 'XYZ');")
C("Find Next", "", "__ok", "AI.findText(str) -> [{frame, index}] (search the stories)", act="var h = AI.findText('text'); var __ok = h.length == 1 && h[0].index == 7;")
C("Recolor Art Dialog", "sel2", "AI.toRGB(R.fillColor).join() == '0,128,0' && AI.toRGB(E.fillColor).join() == '40,90,220'", "AI.recolor(items, [[from, to], ...]) (Recolor Artwork: color mapping)",
  act="AI.recolor([R, E], [[[220, 40, 40], [0, 128, 0]]]);")
C("Colors6", "", "AI.toRGB(R.fillColor).join() == '35,215,215'")
C("Colors5", "sel3", "AI.toRGB(A2.fillColor).join() != '0,150,0'")
C("Colors4", "sel3", "AI.toRGB(A2.fillColor).join() != '0,150,0'")
C("Colors3", "sel3", "AI.toRGB(A2.fillColor).join() != '0,150,0'")
C("Adjust3", "", "AI.toRGB(R.fillColor)[0] < 220 || AI.toRGB(R.fillColor)[1] > 40", "Edit Colors > Adjust Color Balance: menu + dialog (first field typed)", dlg=["sel", "type:-50", "tab", "ok"])
C("Colors8", "", None)
C("Colors9", "cmyk", None)
C("Colors7", "", "R.fillColor.typename == 'GrayColor'")
C("Saturate3", "", "AI.toRGB(R.fillColor).join() != '220,40,40'", "Edit Colors > Saturate: menu + dialog (intensity typed)", dlg=["sel", "type:60", "tab", "ok"])
C("Overprint2", "black", "BK.fillOverprint == true")
# ── Object: transform / arrange / align ─────────────────────────────────────────
C("transformmove", "", "near(AI.box(R).x, 130, 0.6)", "item.translate(dx, dy) / AI.moveTo(); menu: Move dialog (horizontal typed)", dlg=["sel", "type:30", "tab", "sel", "type:0", "tab", "ok"])
C("transformagain", "", "near(AI.box(R).x, 160, 0.6)", "MENU('transformagain') repeats the last menu transform (here Move 30 pt)",
  act="MENU('transformmove'); MENU('transformagain');", dlg=["sel", "type:30", "tab", "sel", "type:0", "tab", "ok"])
C("transformrotate", "", "near(AI.box(R).w, 150, 0.6) && near(AI.box(R).h, 200, 0.6)", "item.rotate(deg) / AI.rotate(); menu: Rotate dialog (angle typed)", dlg=["sel", "type:90", "tab", "ok"])
C("transformreflect", "", None, "item.resize(-100, 100) / AI.flip(); menu: Reflect dialog")
C("transformscale", "", "near(AI.box(R).w, 100, 0.6) && near(AI.box(R).h, 75, 0.6)", "item.resize(sx, sy) / AI.scaleTo(); menu: Scale dialog (uniform % typed)", dlg=["sel", "type:50", "tab", "ok"])
C("transformshear", "", "AI.box(R).w > 250", "item.transform(matrix) with a shear matrix; menu: Shear dialog (angle typed)", dlg=["sel", "type:30", "tab", "ok"])
C("Transform v23", "sel2", "near(AI.box(R).w, 100, 1) && near(AI.box(E).w, 100, 1)", "loop items: item.resize(); menu: Transform Each dialog (horizontal scale typed)",
  dlg=["sel", "type:50", "tab", "sel", "type:50", "tab", "ok"])
C("AI Reset Bounding Box", "rot", "deep:a,b", act="DEEP('a'); MENU('AI Reset Bounding Box'); DEEP('b');")
C("sendToFront", "", "R.absoluteZOrderPosition > E.absoluteZOrderPosition && R.absoluteZOrderPosition > T.absoluteZOrderPosition", "item.zOrder(ZOrderMethod.BRINGTOFRONT)")
C("sendForward", "", "R.absoluteZOrderPosition > E.absoluteZOrderPosition && R.absoluteZOrderPosition < T.absoluteZOrderPosition", "item.zOrder(ZOrderMethod.BRINGFORWARD)")
C("sendBackward", "", "E.absoluteZOrderPosition < R.absoluteZOrderPosition", "item.zOrder(ZOrderMethod.SENDBACKWARD)", act="AI.select([E]); MENU('sendBackward');")
C("sendToBack", "", "T.absoluteZOrderPosition < R.absoluteZOrderPosition", "item.zOrder(ZOrderMethod.SENDTOBACK)", act="AI.select([T]); MENU('sendToBack');")
C("Selection Hat 2", "", "R.layer.name == 'L2'", "item.move(layer, ElementPlacement.PLACEATBEGINNING)",
  act="var L2 = D.layers.add(); L2.name = 'L2'; AI.select([R]); D.activeLayer = L2; MENU('Selection Hat 2');")
X = "[AI.box(A1), AI.box(A2), AI.box(A3)]"
C("Horizontal Align Left", "sel3", f"(function (b) {{ return near(b[0].x, b[1].x) && near(b[1].x, b[2].x); }})({X})", "AI.align(items, 'left')")
C("Horizontal Align Center", "sel3", f"(function (b) {{ return near(b[0].x + b[0].w / 2, b[1].x + b[1].w / 2) && near(b[1].x + b[1].w / 2, b[2].x + b[2].w / 2); }})({X})", "AI.align(items, 'hcenter')")
C("Horizontal Align Right", "sel3", f"(function (b) {{ return near(b[0].x + b[0].w, b[1].x + b[1].w) && near(b[1].x + b[1].w, b[2].x + b[2].w); }})({X})", "AI.align(items, 'right')")
C("Vertical Align Top", "sel3", f"(function (b) {{ return near(b[0].y, b[1].y) && near(b[1].y, b[2].y); }})({X})", "AI.align(items, 'top')")
C("Vertical Align Center", "sel3", f"(function (b) {{ return near(b[0].y + b[0].h / 2, b[1].y + b[1].h / 2) && near(b[1].y + b[1].h / 2, b[2].y + b[2].h / 2); }})({X})", "AI.align(items, 'vcenter')")
C("Vertical Align Bottom", "sel3", f"(function (b) {{ return near(b[0].y + b[0].h, b[1].y + b[1].h) && near(b[1].y + b[1].h, b[2].y + b[2].h); }})({X})", "AI.align(items, 'bottom')")
C("Vertical Distribute Top", "sel3", f"(function (b) {{ return near(b[1].y - b[0].y, b[2].y - b[1].y); }})({X})", "AI.distribute(items, 'v') (top edges)")
C("Vertical Distribute Center", "sel3", f"(function (b) {{ return near(b[1].y + b[1].h / 2 - b[0].y - b[0].h / 2, b[2].y + b[2].h / 2 - b[1].y - b[1].h / 2); }})({X})", "AI.distribute(items, 'v') (centers)")
C("Vertical Distribute Bottom", "sel3", f"(function (b) {{ return near(b[1].y + b[1].h - b[0].y - b[0].h, b[2].y + b[2].h - b[1].y - b[1].h); }})({X})", "AI.distribute(items, 'v') (bottom edges)")
C("Horizontal Distribute Left", "sel3", f"(function (b) {{ return near(b[1].x - b[0].x, b[2].x - b[1].x); }})({X})", "AI.distribute(items, 'h') (left edges)")
C("Horizontal Distribute Center", "sel3", f"(function (b) {{ return near(b[1].x + b[1].w / 2 - b[0].x - b[0].w / 2, b[2].x + b[2].w / 2 - b[1].x - b[1].w / 2); }})({X})", "AI.distribute(items, 'h') (centers)")
C("Horizontal Distribute Right", "sel3", f"(function (b) {{ return near(b[1].x + b[1].w - b[0].x - b[0].w, b[2].x + b[2].w - b[1].x - b[1].w); }})({X})", "AI.distribute(items, 'h') (right edges)")
# ── Object: group / lock / hide / expand ────────────────────────────────────────
C("group", "sel2", "SELT() == 'GroupItem' && D.groupItems.length == 1 && D.groupItems[0].pageItems.length == 2", "AI.group(items)")
C("ungroup", "grp", "D.groupItems.length == 0 && D.pathItems.length == 2", "AI.ungroup(group)")
C("lock", "", "R.locked", "item.locked = true")
C("Selection Hat 5", "", "E.locked && !R.locked", "lock every item above: item.locked = true for absoluteZOrderPosition > n")
C("Selection Hat 7", "", "D.layers.getByName('L2').locked && !R.layer.locked", "layer.locked = true for the other layers",
  act="var L2 = D.layers.add(); L2.name = 'L2'; AI.rect(0, 0, 10, 10).move(L2, ElementPlacement.PLACEATEND); AI.select([R]); MENU('Selection Hat 7');")
C("unlockAll", "", "!R.locked", "item.locked = false (for all)", act="R.locked = true; D.selection = null; MENU('unlockAll');")
C("hide", "", "R.hidden", "item.hidden = true")
C("Selection Hat 4", "", "E.hidden && !R.hidden", "item.hidden = true for items above")
C("Selection Hat 6", "", "!D.layers.getByName('L2').visible && R.layer.visible", "layer.visible = false for the other layers",
  act="var L2 = D.layers.add(); L2.name = 'L2'; AI.rect(0, 0, 10, 10).move(L2, ElementPlacement.PLACEATEND); AI.select([R]); MENU('Selection Hat 6');")
C("showAll", "", "!R.hidden", "item.hidden = false (for all)", act="R.hidden = true; MENU('showAll');")
C("Expand3", "", "SELT() == 'GroupItem' && D.selection[0].pageItems.length == 2", "Object > Expand (dialog accepted): fill and stroke become separate paths")
C("expandStyle", "", "near(AI.box(D.selection[0]).w, 222, 2)", "AI.expandAppearance(item)", act="AI.offsetPath(R, 10); AI.select([R]); MENU('expandStyle');")
C("Crop Image", "img", "AI.box(D.selection[0]).w < 199", "Object > Crop Image: crop widget, then dialog/keys", act="MENU('Crop Image');", dlg="enter")
C("Rasterize 8 menu item", "", "D.rasterItems.length == 1 && D.pathItems.length == __P0 - 1", "document.rasterize(item, bounds, RasterizeOptions) / AI.rasterize()")
C("make mesh", "", "D.meshItems.length == 1", "Object > Create Gradient Mesh (dialog accepted)")
C("AI Object Mosaic Plug-in4", "img", "D.groupItems.length >= 1 && D.groupItems[0].pageItems.length > 10", "Object > Create Object Mosaic (dialog accepted)")
C("TrimMark v25", "", "D.pathItems.length >= __P0 + 8", "Object > Create Trim Marks")
C("Flatten Transparency", "trans", "N('R') == null || R.opacity == 100 || D.groupItems.length > 0", "Object > Flatten Transparency (dialog accepted)")
C("Make Pixel Perfect", "", "R.pixelAligned == true", "item.pixelAligned = true / MENU('Make Pixel Perfect')", act="R.translate(0.37, 0.41); AI.select([R]); MENU('Make Pixel Perfect');")
# slices
C("AISlice Make Slice", "", "R.sliced == true", "item.sliced = true / MENU('AISlice Make Slice')")
C("AISlice Release Slice", "", "R.sliced == false", act="MENU('AISlice Make Slice'); AI.select([R]); MENU('AISlice Release Slice');")
C("AISlice Create from Guides", "guide", "deep:a,b", act="D.selection = null; DEEP('a'); MENU('AISlice Create from Guides'); DEEP('b');")
C("AISlice Create from Selection", "", "deep:a,b", act="DEEP('a'); MENU('AISlice Create from Selection'); DEEP('b');")
C("AISlice Duplicate", "", "deep:a,b", act="MENU('AISlice Create from Selection'); DEEP('a'); MENU('AISlice Duplicate'); DEEP('b');")
C("AISlice Combine", "sel2", "deep:a,b", act="MENU('AISlice Create from Selection'); MENU('selectall'); DEEP('a'); MENU('AISlice Combine'); DEEP('b');")
C("AISlice Divide", "", "deep:a,b", act="MENU('AISlice Create from Selection'); DEEP('a'); MENU('AISlice Divide'); DEEP('b');", dlg=["sel", "type:3", "tab", "ok"])
C("AISlice Delete All Slices", "", "R.sliced == false", act="MENU('AISlice Make Slice'); MENU('AISlice Delete All Slices');")
C("AISlice Slice Options", "", "deep:a,b", act="MENU('AISlice Make Slice'); AI.select([R]); DEEP('a'); MENU('AISlice Slice Options'); DEEP('b');", dlg=["tab", "sel", "type:hero_slice", "tab", "ok"])
C("AISlice Clip to Artboard", "", "deep:a,b", act="MENU('AISlice Make Slice'); DEEP('a'); MENU('AISlice Clip to Artboard'); DEEP('b');")
# path
C("join", "open2", "D.pathItems.length == __P0 - 1", "Object > Path > Join (two open paths)")
C("average", "anchors", "near(R.pathPoints[0].anchor[0], R.pathPoints[1].anchor[0], 0.1) && near(R.pathPoints[0].anchor[1], R.pathPoints[1].anchor[1], 0.1)", "Object > Path > Average (dialog: both axes)")
C("OffsetPath v22", "", "D.pathItems.length > __P0 || D.compoundPathItems.length > 0", "Object > Path > Outline Stroke")
C("OffsetPath v23", "", "D.pathItems.length == __P0 + 1 && AI.box(D.selection[0]).w > 230", "AI.offsetPath(item, d) + AI.expandAppearance(); menu: Offset Path dialog (offset typed)", dlg=["sel", "type:20", "tab", "ok"])
C("Reverse Path Direction", "", "R.pathPoints[1].anchor.join() != a1", act="var a1 = R.pathPoints[1].anchor.join(); MENU('Reverse Path Direction');")
ZZ = "var Z = []; for (var i = 0; i <= 40; i++) Z.push([50 + i * 15, 300 + (i % 2) * 30 + Math.sin(i) * 5]); var ZP = AI.path(Z, {fill: null, stroke: [0, 0, 0], strokeWidth: 2}, {closed: false}); ZP.name = 'ZP'; var z0 = 41; AI.select([ZP]);"
C("simplify menu item", "", "ZP.pathPoints.length < z0", "Object > Path > Simplify (auto simplify)", act=ZZ + "MENU('simplify menu item');")
C("smooth menu item", "", "ZP.pathPoints.length != z0 || ZP.pathPoints[1].leftDirection.join() != ZP.pathPoints[1].anchor.join()", "Object > Path > Smooth", act=ZZ + "MENU('smooth menu item');")
C("Add Anchor Points2", "", "R.pathPoints.length == 8", "Object > Path > Add Anchor Points")
C("Remove Anchor Points menu", "anchors", "R.pathPoints.length == 2", "Object > Path > Remove Anchor Points (selected anchors)")
C("Knife Tool2", "", None, "Object > Path > Divide Objects Below (top object cuts the ones below)", act="AI.select([E]); MENU('Knife Tool2');")
C("Rows and Columns....", "", "D.pathItems.length >= __P0 + 3", "Object > Path > Split Into Grid (dialog: rows 2, columns 2 set through UI Automation)", dlg=["uia:3:2", "uia:7:2", "wait:0.5", "ok"])
C("cleanup menu item", "", "N('SP') == null && N('R') != null", "Object > Path > Clean Up (dialog: stray points, unpainted, empty text)",
  act="var sp = D.pathItems.add(); var pp = sp.pathPoints.add(); pp.anchor = pp.leftDirection = pp.rightDirection = [30, 30]; sp.name = 'SP'; var __P0 = D.pathItems.length; D.selection = null; MENU('cleanup menu item');")
C("Convert to Shape", "", "deep:a,b", "Object > Shape > Convert to Shapes (live shape)", act="DEEP('a'); MENU('Convert to Shape'); DEEP('b');")
C("Expand Shape", "", "deep:b,c", "Object > Shape > Expand Shape", act="MENU('Convert to Shape'); DEEP('b'); AI.select([R]); MENU('Expand Shape'); DEEP('c');")
# pattern
C("Adobe Make Pattern", "", "__pat1 > __pat0", "Object > Pattern > Make (enters pattern mode, adds a swatch); exit with MENU('exitFocus')",
  act="var __pat0 = D.patterns.length; MENU('Adobe Make Pattern'); var __pat1 = app.activeDocument.patterns.length; try { MENU('exitFocus'); } catch (e) {}")
C("Adobe Edit Pattern", "", "__ok", "Object > Pattern > Edit Pattern on a pattern-filled object (pattern mode)",
  act="MENU('Adobe Make Pattern'); try { MENU('exitFocus'); } catch (e) {} var pc = new PatternColor(); pc.pattern = D.patterns[D.patterns.length - 1]; E.fillColor = pc; AI.select([E]); var l0 = D.layers.length; MENU('Adobe Edit Pattern'); var __ok = app.activeDocument.layers.length != l0 || app.activeDocument.layers[0].name != 'Layer 1'; try { MENU('exitFocus'); } catch (e) {}")
# repeat / intertwine / blend
C("Make Radial Repeat", "", "SELT() == 'RadialRepeatItem'", "AI.repeat(item, 'radial')")
C("Make Grid Repeat", "", "SELT() == 'GridRepeatItem'", "AI.repeat(item, 'grid')")
C("Make Symmetry Repeat", "", "SELT() == 'SymmetryRepeatItem'", "AI.repeat(item, 'mirror')")
C("Release Repeat Art", "rep", "D.radialRepeatItems.length == 0")
C("Repeat Art Options", "rep", "deep:a,b", act="DEEP('a'); MENU('Repeat Art Options'); DEEP('b');", dlg=["sel", "type:5", "tab", "ok"])
C("Partial Rearrange Make", "sel2", "deep:a,b", act="DEEP('a'); MENU('Partial Rearrange Make'); DEEP('b');")
C("Partial Rearrange Release", "sel2", "deep:b,c", act="MENU('Partial Rearrange Make'); DEEP('b'); MENU('Partial Rearrange Release'); DEEP('c');")
C("Partial Rearrange Edit", "sel2", "deep:b,c", act="MENU('Partial Rearrange Make'); DEEP('b'); MENU('Partial Rearrange Edit'); DEEP('c');")
C("Path Blend Make", "sel2", "SELT() == 'PluginItem'", "AI.blend([a, b])")
C("Path Blend Release", "blend", "D.pluginItems.length == 0")
C("Path Blend Options", "blend", "deep:a,b", "Object > Blend > Blend Options (dialog: Specified Steps typed)", act="DEEP('a'); MENU('Path Blend Options'); DEEP('b');", dlg=["down", "tab", "sel", "type:3", "tab", "ok"])
C("Path Blend Expand", "blend", "D.pluginItems.length == 0 && D.groupItems.length >= 1")
C("Path Blend Replace Spine", "blend", "deep:a,b", act="var sp = AI.path([[450, 500], [600, 350], [750, 500]], {fill: null, stroke: [0, 0, 0]}, {closed: false}); AI.select([BL, sp]); DEEP('a'); MENU('Path Blend Replace Spine'); DEEP('b');")
C("Path Blend Reverse Spine", "blend", "deep:a,b", act="DEEP('a'); MENU('Path Blend Reverse Spine'); DEEP('b');")
C("Path Blend Reverse Stack", "blend", "deep:a,b", act="DEEP('a'); MENU('Path Blend Reverse Stack'); DEEP('b');")
# envelope
C("Make Warp", "", "SELT() == 'PluginItem'", "Object > Envelope Distort > Make with Warp (dialog accepted) — or AI.warp() as a live effect")
C("Create Envelope Grid", "", "SELT() == 'PluginItem'", "Object > Envelope Distort > Make with Mesh (dialog accepted)")
C("Make Envelope", "sel2", "SELT() == 'PluginItem'", "Object > Envelope Distort > Make with Top Object")
C("Release Envelope", "env", "D.pluginItems.length == 0")
C("Envelope Options", "env", "deep:a,b", act="DEEP('a'); MENU('Envelope Options'); DEEP('b');", dlg=["tab", "tab", "sel", "type:20", "tab", "ok"])
C("Expand Envelope", "env", "D.pluginItems.length == 0 && D.pathItems.length >= 1")
C("Edit Envelope Contents", "env", "SELT() == 'PathItem'")
# perspective
C("Attach to Active Plane", "", "deep:a,b", act="D.showPerspectiveGrid(); AI.select([R]); DEEP('a'); MENU('Attach to Active Plane'); DEEP('b');")
C("Release with Perspective", "", "deep:b,c", act="D.showPerspectiveGrid(); AI.select([R]); MENU('Attach to Active Plane'); DEEP('b'); AI.select([R]); MENU('Release with Perspective'); DEEP('c');")
C("Show Object Grid Plane", "", "deep:b,c", act="D.showPerspectiveGrid(); AI.select([R]); MENU('Attach to Active Plane'); DEEP('b'); AI.select([R]); MENU('Show Object Grid Plane'); DEEP('c');")
C("Edit Original Object", "", "deep:b,c", act="D.showPerspectiveGrid(); AI.select([T]); MENU('Attach to Active Plane'); DEEP('b'); AI.select([D.selection[0]]); MENU('Edit Original Object'); DEEP('c'); try { MENU('exitFocus'); } catch (e) {}")
# live paint
C("Make Planet X", "sel2", "SELT() == 'PluginItem'", "Object > Live Paint > Make")
C("Marge Planet X", "lp", "deep:a,b", act="var nx = AI.rect(500, 380, 60, 60, {fill: [0, 200, 0]}); AI.select([LP, nx]); DEEP('a'); MENU('Marge Planet X'); DEEP('b');")
C("Release Planet X", "lp", "D.pluginItems.length == 0")
C("Planet X Options", "lp", "deep:a,b", act="DEEP('a'); MENU('Planet X Options'); DEEP('b');", dlg=["tab", "space", "ok"])
C("Expand Planet X", "lp", "D.pluginItems.length == 0 && D.groupItems.length >= 1")
# image trace
C("Make Image Tracing", "img", "SELT() == 'PluginItem' && D.selection[0].isTracing", "rasterOrPlaced.trace() / AI.trace()")
C("Make and Expand Image Tracing", "img", "D.pluginItems.length == 0 && D.pathItems.length > __P0 + 1", "AI.trace(item, preset, true)")
C("Release Image Tracing", "trace", "SELT() == 'RasterItem'", "tracing.releaseTracing()")
C("Expand Image Tracing", "trace", "D.pluginItems.length == 0 && D.groupItems.length >= 1", "tracing.expandTracing()")
# text wrap / masks / compound
C("Make Text Wrap", "area", "R.wrapped == true", "item.wrapped = true", act="AI.select([R]); MENU('Make Text Wrap');")
C("Release Text Wrap", "area", "R.wrapped == false", "item.wrapped = false", act="AI.select([R]); MENU('Make Text Wrap'); AI.select([R]); MENU('Release Text Wrap');")
C("Text Wrap Options...", "area", "near(R.wrapOffset, 17, 0.1)", "item.wrapOffset / wrapInside", act="AI.select([R]); MENU('Make Text Wrap'); AI.select([R]); MENU('Text Wrap Options...');", dlg=["sel", "type:17", "tab", "ok"])
C("makeMask", "sel2", "D.groupItems.length == 1 && D.groupItems[0].clipped", "AI.clip(mask, items)")
C("releaseMask", "clip", "D.groupItems.length == 0 || !D.groupItems[0].clipped")
C("editMask", "clip", "NS() == 1 && SELT() == 'PathItem'", "Object > Clipping Mask > Edit Mask (the mask path gets selected)")
C("compoundPath", "sel2", "D.compoundPathItems.length == 1", "AI.compound(paths)")
C("noCompoundPath", "cmp", "D.compoundPathItems.length == 0")
# artboards
C("setCropMarks", "", "D.artboards.length == 2", "document.artboards.add(rect) / AI.addArtboard()")
C("ReArrange Artboards", "", "deep:a,b", "document.rearrangeArtboards(layout, rowsOrCols, spacing, moveArtwork)", act="AI.addArtboard(900, 0, 100, 100); DEEP('a'); MENU('ReArrange Artboards'); DEEP('b');", dlg=["tab", "tab", "sel", "type:80", "tab", "ok"])
C("Fit Artboard to artwork bounds", "", "AI.ab(0).w < 790", "AI.fitArtboard(i)")
C("Fit Artboard to selected Art", "", "AI.ab(0).w < 210", "document.fitArtboardToSelectedArt(i) / AI.fitArtboard(i, items)")
C("collectForExportSingleAsset", "sel2", "D.assets.length == 1", "document.assets.add(item)")
C("collectForExportMultipleAsset", "sel2", "D.assets.length == 2", "document.assets.add(item) per item")
# graph (needs a graph object: tests/fixtures/graph.ai is made once by tools/make_graph_fixture.py)
GRAPH = "var gf = new File(SKILL + '/tests/fixtures/graph.ai'); D.close(SaveOptions.DONOTSAVECHANGES); D = app.open(gf); var GR0 = D.graphItems[0]; AI.select([GR0]); DEEP('a');"
C("setGraphStyle", "none", "deep:a,b", "Object > Graph > Type (dialog: chart type)", act=GRAPH + "MENU('setGraphStyle'); DEEP('b');", dlg=["tab", "space", "ok"])
C("editGraphData", "none", "__ok", "Object > Graph > Data (opens the data window)", act=GRAPH + "MENU('editGraphData'); var __ok = true;")
C("graphDesigns", "none", "deep:a,b", "Object > Graph > Design (new design from selection)", act=GRAPH.replace("var GR0", "var dz = AI.rect(700, 500, 30, 30, {fill: [0, 128, 0]}); AI.select([dz]); var GR0") + "AI.select([dz]); MENU('graphDesigns'); DEEP('b');", dlg=["tab", "space", "ok"])
C("setBarDesign", "none", "deep:a,b", "Object > Graph > Column", act=GRAPH + "MENU('setBarDesign'); DEEP('b');", dlg=["down", "ok"])
C("setIconDesign", "none", "deep:a,b", "Object > Graph > Marker", act=GRAPH + "MENU('setIconDesign'); DEEP('b');", dlg=["down", "ok"])
# ── Type ──────────────────────────────────────────────────────────────────────
C("point-area", "txt", "T.kind == TextType.AREATEXT", "textFrame.convertPointObjectToAreaObject()")
C("areatextoptions", "area", "AT.columnCount == 2 && near(AT.columnGutter, 18, 0.1)", "textFrame.columnCount / rowCount / columnGutter / rowGutter / spacing / firstBaseline",
  act="AT.columnCount = 2; AT.columnGutter = 18;")
for c in ["textpathtypeRainbow", "textpathtypeSkew", "textpathtype3d", "textpathtypestairs", "textpathtypeGravity"]:
    C(c, "pathtxt", "deep:a,b", f"Type > Type on a Path > {c[12:]}", act=f"DEEP('a'); MENU('{c}'); DEEP('b');")
C("textpathtypeOptions", "pathtxt", "deep:a,b", act="DEEP('a'); MENU('textpathtypeOptions'); DEEP('b');", dlg=["down", "ok"])
C("threadTextCreate", "area", "AT.nextFrame != null", "Type > Threaded Text > Create (area text + an empty path)",
  act="var fr = AI.rect(450, 520, 250, 60, {fill: null, stroke: null}); AI.select([AT, fr]); MENU('threadTextCreate');")
C("releaseThreadedTextSelection", "area", "AT.nextFrame == null", act="var fr = AI.rect(450, 520, 250, 60, {fill: null, stroke: null}); AI.select([AT, fr]); MENU('threadTextCreate'); AI.select([AT.nextFrame]); MENU('releaseThreadedTextSelection');")
C("removeThreading", "area", "AT.nextFrame == null", act="var fr = AI.rect(450, 520, 250, 60, {fill: null, stroke: null}); AI.select([AT, fr]); MENU('threadTextCreate'); AI.select([AT]); MENU('removeThreading');")
C("fitHeadline", "area", "!near(AT.textRange.characterAttributes.size, 16, 0.01) || AT.textRange.characterAttributes.tracking != 0", "Type > Fit Headline (area text, cursor in the paragraph)",
  act="AT.contents = 'Headline'; AT.paragraphs[0].select(); MENU('fitHeadline');")
C("Adobe Illustrator Find Font Menu Item", "", "T.textRange.characterAttributes.textFont.name == 'Arial-BoldMT'", "characterAttributes.textFont = app.textFonts.getByName(...) (Find/Replace Font)",
  act="var f = AI.font('Arial-BoldMT'); for (var i = 0; i < D.textFrames.length; i++) D.textFrames[i].textRange.characterAttributes.textFont = f;")
C("UpperCase Change Case Item", "txt", "T.contents == 'SAMPLE TEXT ABC'")
C("LowerCase Change Case Item", "txt", "T.contents == 'sample text abc'", act="T.contents = 'SAMPLE Text ABC'; AI.select([T]); MENU('LowerCase Change Case Item');")
C("Title Case Change Case Item", "txt", "T.contents == 'Sample Text Abc'")
C("Sentence case Change Case Item", "txt", "T.contents == 'Hello world again'", act="T.contents = 'hELLO WORLD AGAIN'; AI.select([T]); MENU('Sentence case Change Case Item');")
C("Adobe Illustrator Smart Punctuation Menu Item", "txt", "T.contents.indexOf('\\u201C') >= 0 || T.contents.indexOf('\\u2019') >= 0", "Type > Smart Punctuation (dialog accepted)",
  act="T.contents = '\"quoted\" it\\'s'; AI.select([T]); MENU('Adobe Illustrator Smart Punctuation Menu Item');")
C("outline", "txt", "D.textFrames.length == 0 && SELT() == 'GroupItem'", "textFrame.createOutline() / AI.outline()")
C("Adobe Optical Alignment Item", "area", "AT.opticalAlignment == true", "textFrame.opticalAlignment = true")
SPECIAL = {"~bullet": "\\u2022", "~copyright": "\\u00A9", "~ellipsis": "\\u2026", "~paragraphSymbol": "\\u00B6", "~registeredTrademark": "\\u00AE", "~sectionSymbol": "\\u00A7",
           "~trademarkSymbol": "\\u2122", "~emDash": "\\u2014", "~enDash": "\\u2013", "~discretionaryHyphen": "\\u00AD", "~doubleLeftQuote": "\\u201C",
           "~doubleRightQuote": "\\u201D", "~singleLeftQuote": "\\u2018", "~singleRightQuote": "\\u2019", "~emSpace": "\\u2003", "~enSpace": "\\u2002",
           "~hairSpace": "\\u200A", "~thinSpace": "\\u2009", "~forcedLineBreak": "\\u0003"}
for c, u in SPECIAL.items():
    C(c, "txtip", f"T.contents.indexOf('{u}') == 6 || T.contents.charAt(6) != 'e'", f"insert the character into contents ('{u}'), or MENU('{c}') with the cursor / a selection in the text")
C("~placeHolderText", "area", "AT.contents.length > 30 && AT.contents.indexOf('Area text') < 0", act="AT.contents = 'x'; AT.textRange.characters[0].select(); MENU('~placeHolderText');")
C("type-horizontal", "txt", "T.orientation == TextOrientation.HORIZONTAL", "textFrame.orientation = TextOrientation.HORIZONTAL", act="T.orientation = TextOrientation.VERTICAL; AI.select([T]); MENU('type-horizontal');")
C("type-vertical", "txt", "T.orientation == TextOrientation.VERTICAL", "textFrame.orientation = TextOrientation.VERTICAL")
LEG = "var lf = new File(TMP + '/_legacy8.ai'); var o = new IllustratorSaveOptions(); o.compatibility = Compatibility.ILLUSTRATOR8; D.saveAs(lf, o); D.close(SaveOptions.DONOTSAVECHANGES); D = app.open(lf); var __L0 = D.legacyTextItems.length;"
C("convertlegacyText", "none", "__L0 > 0 && D.legacyTextItems.length < __L0", "legacyTextItems[i].convertToNative() / Type > Legacy Text > Update All", act=LEG + "MENU('convertlegacyText');", dlg="esc")
C("convertlegacyText1", "none", "__L0 > 0 && D.legacyTextItems.length < __L0", "legacyTextItem.convertToNative()", act=LEG + "AI.select([D.legacyTextItems[0]]); MENU('convertlegacyText1');", dlg="esc")
C("convertlegacyText2", "none", "deep:a,b", act=LEG + "D.legacyTextItems[0].convertToNative(); DEEP('a'); MENU('convertlegacyText2'); DEEP('b');", dlg="esc")
C("convertlegacyText3", "none", "D.pageItems.length < __n1", act=LEG + "D.legacyTextItems[0].convertToNative(); var __n1 = D.pageItems.length; MENU('convertlegacyText3');", dlg="esc")
C("convertlegacyText4", "none", "NS() > 0", act=LEG + "D.legacyTextItems[0].convertToNative(); D.selection = null; MENU('convertlegacyText4');", dlg="esc")
# ── Select ────────────────────────────────────────────────────────────────────
C("selectall", "none", "NS() == 3", "item.selected = true for every item / document.selection = items")
C("selectallinartboard", "none", "NS() == 3", "document.selectObjectsOnActiveArtboard()", act="AI.rect(900, 100, 50, 50); D.selection = null; MENU('selectallinartboard');")
C("deselectall", "", "NS() == 0", "document.selection = null")
C("Find Reselect menu item", "", "R2.selected", act="var R2 = AI.rect(500, 400, 50, 50, {fill: [220, 40, 40]}); R2.name = 'R2'; AI.select([R]); MENU('Find Fill Color menu item'); D.selection = null; AI.select([R]); MENU('Find Reselect menu item');")
C("Inverse menu item", "", "NS() == 2 && !R.selected", "select every item that is not selected")
C("Selection Hat 8", "", "E.selected && !R.selected", "select the item with the next higher absoluteZOrderPosition")
C("Selection Hat 9", "", "R.selected && !E.selected", "select the item with the next lower absoluteZOrderPosition", act="AI.select([E]); MENU('Selection Hat 9');")


def SAME(cmd, prep, how):
    C(cmd, "", "R2.selected && !E.selected", how, act=prep + f" AI.select([R]); MENU('{cmd}');")


R2 = "var R2 = AI.rect(500, 400, 80, 80,  {fill: [220, 40, 40], stroke: [20, 20, 20], strokeWidth: 2}); R2.name = 'R2';"
SAME("Find Appearance menu item", R2, "compare appearance (fill, stroke, effects) and select matches")
SAME("Find Appearance Attributes menu item", "AI.roundCorners(R, 7); var R2 = AI.rect(500, 400, 80, 80,  {fill: [0, 200, 0], stroke: null}); R2.name = 'R2'; AI.roundCorners(R2, 7);", "select items sharing a live effect")
SAME("Find Blending Mode menu item", "R.blendingMode = BlendModes.MULTIPLY; var R2 = AI.rect(500, 400, 80, 80,  {fill: [0, 200, 0], blend: 'multiply'}); R2.name = 'R2';", "select items with the same blendingMode")
SAME("Find Fill & Stroke menu item", R2, "select items with equal fillColor and strokeColor")
SAME("Find Fill Color menu item", "var R2 = AI.rect(500, 400, 80, 80,  {fill: [220, 40, 40], stroke: null}); R2.name = 'R2';", "select items with equal fillColor")
SAME("Find Opacity menu item", "R.opacity = 40; var R2 = AI.rect(500, 400, 80, 80,  {fill: [0, 200, 0], opacity: 40}); R2.name = 'R2';", "select items with equal opacity")
SAME("Find Stroke Color menu item", "var R2 = AI.rect(500, 400, 80, 80,  {fill: [0, 200, 0], stroke: [20, 20, 20], strokeWidth: 9}); R2.name = 'R2';", "select items with equal strokeColor")
SAME("Find Stroke Weight menu item", "var R2 = AI.rect(500, 400, 80, 80,  {fill: [0, 200, 0], stroke: [0, 0, 250], strokeWidth: 2}); R2.name = 'R2';", "select items with equal strokeWidth")
SAME("Find Style menu item", "var gs = D.graphicStyles[1]; gs.applyTo(R); var R2 = AI.rect(500, 400, 80, 80); R2.name = 'R2'; gs.applyTo(R2);", "select items with the same graphic style")
SAME("Find Live Shape menu item", "AI.select([R]); MENU('Convert to Shape'); var R2 = AI.rect(500, 400, 80, 40, {fill: [0, 200, 0]}); R2.name = 'R2'; AI.select([R2]); MENU('Convert to Shape');", "select live shapes of the same kind")
C("Find Symbol Instance menu item", "sym", "NS() == 2", "select symbolItems whose .symbol is the same", act="var s2 = D.symbolItems.add(SY.symbol); AI.select([SY]); MENU('Find Symbol Instance menu item');")
C("Find Link Block Series menu item", "area", "NS() == 2", "select the frames of one story (textFrame.story.textFrames)",
  act="var fr = AI.rect(450, 520, 250, 60, {fill: null, stroke: null}); AI.select([AT, fr]); MENU('threadTextCreate'); AI.select([AT]); MENU('Find Link Block Series menu item');")
TX2 = "var T2 = AI.text('Another', 500, 500, {size: 36}); T2.name = 'T2'; var T3 = AI.text('Third', 500, 300, {size: 20, font: 'Arial-BoldMT'}); T3.name = 'T3'; AI.select([T]);"
for c, chk in [("Find Text Font Family menu item", "T2.selected"), ("Find Text Font Family Style menu item", "T2.selected"),
               ("Find Text Font Family Style Size menu item", "T2.selected && !T3.selected"), ("Find Text Font Size menu item", "T2.selected && !T3.selected"),
               ("Find Text Fill Color menu item", "T2.selected"), ("Find Text Stroke Color menu item", "T2.selected"), ("Find Text Fill Stroke Color menu item", "T2.selected")]:
    C(c, "", chk, "compare characterAttributes (textFont, size, fillColor, strokeColor) across textFrames", act=TX2 + f"MENU('{c}');")
C("Selection Hat 3", "", "NS() == 3", "select every item of item.layer")
C("Selection Hat 1", "", "R.pathPoints[0].selected == PathPointSelection.ANCHORPOINT || R.pathPoints[0].selected != PathPointSelection.NOSELECTION", "pathPoint.selected = PathPointSelection.*")
C("Bristle Brush Strokes menu item", "none", "NS() >= 1", act="var bp = AI.line(50, 550, 400, 550); bp.name = 'BP'; var bb = null; for (var i = 0; i < D.brushes.length; i++) if (/bristle|鬃毛/i.test(D.brushes[i].name)) bb = D.brushes[i]; if (!bb) { MENU('Adobe BrushManager Menu Item'); } if (bb) bb.applyTo(bp); D.selection = null; MENU('Bristle Brush Strokes menu item');")
C("Brush Strokes menu item", "none", "NS() >= 1 && bp.selected", "brush.applyTo(path); select paths that have a brush", act="var bp = AI.line(50, 550, 400, 550); bp.name = 'BP'; D.brushes[1].applyTo(bp); D.selection = null; MENU('Brush Strokes menu item');")
C("Clipping Masks menu item", "clip+none", "NS() == 1 && D.selection[0].clipping", "select pathItems with clipping == true", act="D.selection = null; MENU('Clipping Masks menu item');")
C("Stray Points menu item", "none", "NS() == 1 && D.selection[0].name == 'SP'", "select pathItems with a single point", act="var sp = D.pathItems.add(); var pp = sp.pathPoints.add(); pp.anchor = pp.leftDirection = pp.rightDirection = [30, 30]; sp.name = 'SP'; D.selection = null; MENU('Stray Points menu item');")
C("Text Objects menu item", "area+none", "NS() == 2", "select every textFrame")
C("Point Text Objects menu item", "area+none", "NS() == 1 && D.selection[0].kind == TextType.POINTTEXT", "select textFrames with kind POINTTEXT")
C("Area Text Objects menu item", "area+none", "NS() == 1 && D.selection[0].kind == TextType.AREATEXT", "select textFrames with kind AREATEXT")
C("SmartEdit Menu Item", "", "D.isSmartEditMode() == true", "Select > Start Global Edit", act="var R2 = AI.rect(500, 400, 200, 150, {fill: [220, 40, 40], stroke: [20, 20, 20], strokeWidth: 2}); R2.name = 'R2'; AI.select([R]); MENU('SmartEdit Menu Item');")
C("Selection Hat 10", "", "deep:a,b", "Select > Save Selection (name typed)", act="DEEP('a'); MENU('Selection Hat 10'); DEEP('b');", dlg=["sel", "type:MySel", "tab", "ok"])
C("Selection Hat 11", "", "deep:b,c", "Select > Edit Selection (rename typed)", act="MENU('Selection Hat 10'); DEEP('b'); MENU('Selection Hat 11'); DEEP('c');", dlg=["sel", "type:MySel", "tab", "ok"])
C("Selection Hat 14", "", "deep:b,c", "Select > Update Selection", act="MENU('Selection Hat 10'); DEEP('b'); AI.select([R, E]); MENU('Selection Hat 14'); DEEP('c');", dlg=["sel", "type:MySel", "tab", "ok"])
# ── Effect (menu-level; each effect itself: tests/effects_sweep.py) ────────────
C("Adobe Apply Last Effect", "", "deep:a,b", act="MENU('Live Roughen'); AI.select([E]); DEEP('a'); MENU('Adobe Apply Last Effect'); DEEP('b');")
C("Adobe Last Effect", "", "deep:a,b", act="MENU('Live Roughen'); AI.select([E]); DEEP('a'); MENU('Adobe Last Effect'); DEEP('b');")
C("Live Rasterize Effect Setting", "", "D.rasterEffectSettings.resolution == 300", "document.rasterEffectSettings.resolution / .transparency / .padding ...",
  act="D.rasterEffectSettings.resolution = 300;")
# ── View (only what reads back through the DOM) ────────────────────────────────
C("preview", "", "D.isOutlineMode() == true", "View > Outline (readback document.isOutlineMode())")
C("ink", "", "D.getPreviewMode() != m0", "View > Overprint Preview (readback document.getPreviewMode())", act="var m0 = D.getPreviewMode(); MENU('ink');")
C("raster", "", "D.getPreviewMode() != m0", "View > Pixel Preview (readback document.getPreviewMode())", act="var m0 = D.getPreviewMode(); MENU('raster');")
C("TrimView", "", "D.isTrimViewEnabled() == true", "View > Trim View (readback document.isTrimViewEnabled())")
C("zoomin", "", "D.activeView.zoom > z0", "document.activeView.zoom", act="var z0 = D.activeView.zoom; MENU('zoomin');")
C("zoomout", "", "D.activeView.zoom < z0", "document.activeView.zoom", act="var z0 = D.activeView.zoom; MENU('zoomout');")
C("fitin", "", "!near(D.activeView.zoom, 3, 0.01) && D.activeView.zoom > 0", "document.activeView.zoom", act="var z0 = D.activeView.zoom; D.activeView.zoom = 3; MENU('fitin');")
C("fitall", "", "D.activeView.zoom < 3", "document.activeView.zoom", act="AI.addArtboard(900, 0, 800, 600); D.activeView.zoom = 3; MENU('fitall');")
C("actualsize", "", "near(D.activeView.visibleZoom, 1, 0.01)", "view.visibleZoom reads 1 (view.zoom is scaled by the display DPI: 1.5 at 150%)", act="D.activeView.zoom = 2.5; MENU('actualsize');")
for a in ["180", "150", "135", "120", "90", "60", "45", "30", "15"]:
    C(f"RotateView{a}", "", f"near(Math.abs(D.activeView.rotateAngle), {a}, 0.5)", "document.activeView.rotateAngle")
for a in ["15", "30", "45", "60", "90", "120", "135", "150", "180"]:
    C(f"RotateViewNegative{a}", "", f"near(Math.abs(D.activeView.rotateAngle), {a}, 0.5)", "document.activeView.rotateAngle")
C("RotateViewZero", "", "near(D.activeView.rotateAngle, 0, 0.1)", "document.activeView.rotateAngle = 0", act="MENU('RotateView45'); MENU('RotateViewZero');")
C("resetRotationView", "", "near(D.activeView.rotateAngle, 0, 0.1)", "document.activeView.rotateAngle = 0", act="MENU('RotateView45'); MENU('resetRotationView');")
C("rotateViewToSelection", "rot", "!near(D.activeView.rotateAngle, 0, 0.1)", "View > Rotate View to Selection (readback activeView.rotateAngle)")
C("TransparencyGrid Menu Item", "", "D.isTransparencyGridVisible() != g0", "View > Transparency Grid (readback document.isTransparencyGridVisible())", act="var g0 = D.isTransparencyGridVisible(); MENU('TransparencyGrid Menu Item');")
C("ruler", "", "D.isRulerVisible() != r0", "View > Rulers (readback document.isRulerVisible())", act="var r0 = D.isRulerVisible(); MENU('ruler');")
C("showguide", "", "D.isGuideVisible() != g0", "View > Guides (readback document.isGuideVisible())", act="var g0 = D.isGuideVisible(); MENU('showguide');")
C("makeguide", "", "R.guides == true", "pathItem.guides = true")
C("releaseguide", "guide", "GD.guides == false", "pathItem.guides = false")
C("clearguide", "guide", "N('GD') == null", "remove every pathItem with guides == true")
C("lockguide", "guide", "deep:a,b", act="DEEP('a'); MENU('lockguide'); DEEP('b');")
C("showgrid", "", "D.isGridVisible() != g0", "View > Show Grid (readback document.isGridVisible())", act="var g0 = D.isGridVisible(); MENU('showgrid');")
C("Show Perspective Grid", "", "deep:a,b", "document.showPerspectiveGrid() / hidePerspectiveGrid()", act="DEEP('a'); MENU('Show Perspective Grid'); DEEP('b');")
C("newview", "", "deep:a,b", "View > New View (name typed)", act="DEEP('a'); MENU('newview'); DEEP('b');", dlg=["sel", "type:SweepView", "tab", "ok"])
C("newwindow", "", "D.views.length == 2", "Window > New Window (readback document.views.length)")
# ── Keyboard-only commands that change the document ────────────────────────────
C("leftAlign", "area", "AT.textRange.paragraphAttributes.justification == Justification.LEFT", "paragraphAttributes.justification", act="AT.textRange.paragraphAttributes.justification = Justification.RIGHT; AI.select([AT]); MENU('leftAlign');")
C("centerAlign", "area", "AT.textRange.paragraphAttributes.justification == Justification.CENTER", "paragraphAttributes.justification")
C("rightAlign", "area", "AT.textRange.paragraphAttributes.justification == Justification.RIGHT", "paragraphAttributes.justification")
C("justify", "area", "AT.textRange.paragraphAttributes.justification == Justification.FULLJUSTIFYLASTLINELEFT", "paragraphAttributes.justification")
C("justifyCenter", "area", "AT.textRange.paragraphAttributes.justification == Justification.FULLJUSTIFYLASTLINECENTER", "paragraphAttributes.justification")
C("justifyRight", "area", "AT.textRange.paragraphAttributes.justification == Justification.FULLJUSTIFYLASTLINERIGHT", "paragraphAttributes.justification")
C("justifyAll", "area", "AT.textRange.paragraphAttributes.justification == Justification.FULLJUSTIFY", "paragraphAttributes.justification")
C("sizeStepUp", "txt", "T.textRange.characterAttributes.size > 36", "characterAttributes.size")
C("sizeStepDown", "txt", "T.textRange.characterAttributes.size < 36", "characterAttributes.size")
C("faceSizeUp", "txt", "T.textRange.characterAttributes.size > 36", "characterAttributes.size")
C("faceSizeDown", "txt", "T.textRange.characterAttributes.size < 36", "characterAttributes.size")
C("~kernFurther", "txtr", "T.textRange.characterAttributes.tracking > 0", "characterAttributes.tracking")
C("~kernCloser", "txtr", "T.textRange.characterAttributes.tracking < 0", "characterAttributes.tracking")
C("tracking", "txtr", "T.textRange.characterAttributes.tracking != 0", "characterAttributes.tracking")
C("clearTrack", "txtr", "T.textRange.characterAttributes.tracking == 0", "characterAttributes.tracking = 0", act="T.textRange.characterAttributes.tracking = 200; T.textRange.select(); MENU('clearTrack');")
C("clearTypeScale", "txtr", "T.textRange.characterAttributes.horizontalScale == 100", "characterAttributes.horizontalScale / verticalScale = 100",
  act="T.textRange.characterAttributes.horizontalScale = 150; T.textRange.select(); MENU('clearTypeScale');")
C("~superScript", "txtr", "T.textRange.characterAttributes.baselinePosition == FontBaselineOption.SUPERSCRIPT", "characterAttributes.baselinePosition = FontBaselineOption.SUPERSCRIPT")
C("~subscript", "txtr", "T.textRange.characterAttributes.baselinePosition == FontBaselineOption.SUBSCRIPT", "characterAttributes.baselinePosition = FontBaselineOption.SUBSCRIPT")
C("toggleAutoHyphen", "area", "AT.textRange.paragraphAttributes.hyphenation != h0", "paragraphAttributes.hyphenation", act="var h0 = AT.textRange.paragraphAttributes.hyphenation; AI.select([AT]); MENU('toggleAutoHyphen');")
C("toggleLineComposer", "area", "AT.textRange.paragraphAttributes.everyLineComposer != c0", "paragraphAttributes.everyLineComposer", act="var c0 = AT.textRange.paragraphAttributes.everyLineComposer; AI.select([AT]); MENU('toggleLineComposer');")
C("lock2", "", "E.locked && T.locked && !R.locked", "lock every unselected item (item.locked = true)")
C("hide2", "", "E.hidden && T.hidden && !R.hidden", "hide every unselected item (item.hidden = true)")
C("repeatPathfinder", "sel2", "D.pathItems.length == __P0 - 1 || D.compoundPathItems.length == 1", "repeat the last Pathfinder panel operation",
  act="MENU('Live Pathfinder Add'); MENU('expandStyle'); var a = AI.rect(500, 400, 60, 60), b = AI.rect(530, 430, 60, 60); var __P0 = D.pathItems.length; AI.select([a, b]); MENU('repeatPathfinder');")
C("avgAndJoin", "open2", "D.pathItems.length == __P0 - 1", "Average and Join (two open endpoints)", act="P1.pathPoints[1].selected = PathPointSelection.ANCHORPOINT; P2.pathPoints[0].selected = PathPointSelection.ANCHORPOINT; P1.selected = false; P2.selected = false; P1.pathPoints[1].selected = PathPointSelection.ANCHORPOINT; P2.pathPoints[0].selected = PathPointSelection.ANCHORPOINT; MENU('avgAndJoin');")
C("enterFocus", "grp", "deep:a,b", "enter isolation mode on the selected group", act="DEEP('a'); MENU('enterFocus'); DEEP('b'); MENU('exitFocus');")
C("exitFocus", "grp", "__ok", "exit isolation mode", act="MENU('enterFocus'); var inIso = app.activeDocument.layers.length; MENU('exitFocus'); var __ok = true;")
C("Adobe New Fill Shortcut", "", "deep:a,b", "Appearance: add new fill", act="DEEP('a'); MENU('Adobe New Fill Shortcut'); DEEP('b');")
C("Adobe New Stroke Shortcut", "", "deep:a,b", "Appearance: add new stroke", act="DEEP('a'); MENU('Adobe New Stroke Shortcut'); DEEP('b');")
C("Adobe New Style Shortcut", "", "D.graphicStyles.length > g0", "Graphic Styles: new style from selection", act="var g0 = D.graphicStyles.length; MENU('Adobe New Style Shortcut');")
C("AdobeLayerPalette2", "", "D.layers.length == 2", "document.layers.add()")
C("AdobeLayerPalette3", "", "D.layers.length == 2", "document.layers.add() (+ options dialog)")
C("Adobe New Swatch Shortcut Menu", "", "D.swatches.length > s0", "document.swatches.add()", act="var s0 = D.swatches.length; MENU('Adobe New Swatch Shortcut Menu');")
C("Adobe New Symbol Shortcut", "", "D.symbols.length == s0 + 1", "document.symbols.add(item)", act="var s0 = D.symbols.length; MENU('Adobe New Symbol Shortcut');")
C("Adobe Update Link Shortcut", "placed", "__ok", "placedItem.relink(file) / update after the file changed",
  act="var f = PL.file; var d0 = app.activeDocument; var d2 = NEWDOC(200, 150, 'x'); AI.rect(0, 0, 200, 150, {fill: [0, 200, 0]}); AI.png(f.fsName); d2.close(SaveOptions.DONOTSAVECHANGES); d0.activate(); AI.select([PL]); MENU('Adobe Update Link Shortcut'); var __ok = true;")
# ── added: remaining commands ─────────────────────────────────────────────────
C("assignprofile", "", "deep:a,b", "Edit > Assign Profile (dialog: 'Don't Color Manage' chosen)", act="DEEP('a'); MENU('assignprofile'); DEEP('b');", dlg=["up", "up", "up", "ok"])
C("updateLegacyTOP", "pathtxt+none", "deep:a,b", "Type > Type on a Path > Update Legacy Type on a Path (legacy file)",
  act="var lf = new File(TMP + '/_legacytop.ai'); var o = new IllustratorSaveOptions(); o.compatibility = Compatibility.ILLUSTRATOR8; D.saveAs(lf, o); D.close(SaveOptions.DONOTSAVECHANGES); D = app.open(lf); if (D.legacyTextItems.length) D.legacyTextItems[0].convertToNative(); AI.select([D.pageItems[0]]); DEEP('a'); MENU('updateLegacyTOP'); DEEP('b');", dlg="esc")
C("SVG Filter Import", "", "deep:a,b", "Effect > SVG Filters > Import SVG Filter (file typed into the open dialog)",
  act="var sf = new File(TMP + '/_filters.svg'); sf.encoding = 'UTF-8'; sf.open('w'); sf.write('<svg xmlns=\"http://www.w3.org/2000/svg\"><defs><filter id=\"SweepBlur\"><feGaussianBlur stdDeviation=\"3\"/></filter></defs></svg>'); sf.close(); DEEP('a'); MENU('SVG Filter Import'); DEEP('b');",
  dlg=["edit:0:{TMPW}\\_filters.svg", "wait:0.3", "ok"])
C("spacing", "txtr", "deep:a,b", "word spacing shortcut (paragraphAttributes.desiredWordSpacing)", act="DEEP('a'); MENU('spacing'); DEEP('b');")


# ── Commands whose menu ID refuses scripts here: app.executeMenuCommand throws PARM (the same error as an unknown name)
#    even with the right selection. Where the DOM does the same thing, that route is verified instead (marked in "how").
def R(cmd, kind, check, how, act, dlg="esc"):
    how = how + " [menu ID refuses scripts: PARM]"
    for c in CASES:
        if c["cmd"] == cmd:
            c.update({"kind": kind, "check": check, "how": how, "act": act, "dlg": dlg})
            return
    C(cmd, kind, check, how, act=act, dlg=dlg)


def FIX(cmd, **kw):
    for c in CASES:
        if c["cmd"] == cmd:
            c.update(kw)


FIX("saveasTemplate", act="var tf = new File(TMP + '/_tpl.ait'); if (tf.exists) tf.remove(); MENU('saveastemplate');",
    how="MENU('saveastemplate') (the shortcut set spells it saveasTemplate) + save dialog (path typed)")
R("point-area", "txt", "T.kind == TextType.AREATEXT", "textFrame.convertPointObjectToAreaObject()", "T = T.convertPointObjectToAreaObject();")
for a in ["180", "150", "135", "120", "90", "60", "45", "30", "15"]:
    R(f"RotateView{a}", "", f"near(D.activeView.rotateAngle, {a}, 0.5)", f"document.activeView.rotateAngle = {a} (the menu needs GPU Preview)", f"D.activeView.rotateAngle = {a};")
    R(f"RotateViewNegative{a}", "", f"near(D.activeView.rotateAngle, -{a}, 0.5) || near(D.activeView.rotateAngle, 360 - {a}, 0.5)",
      f"document.activeView.rotateAngle = -{a}", f"D.activeView.rotateAngle = -{a};")
for c in ["RotateViewZero", "resetRotationView"]:
    R(c, "", "near(D.activeView.rotateAngle, 0, 0.1)", "document.activeView.rotateAngle = 0", "D.activeView.rotateAngle = 45; D.activeView.rotateAngle = 0;")
R("rotateViewToSelection", "rot", "near(D.activeView.rotateAngle, 30, 0.5)", "document.activeView.rotateAngle = the item's rotation (30 deg here)", "D.activeView.rotateAngle = 30;")
for c, u in SPECIAL.items():
    R(c, "txt", f"T.contents.charAt(6) == '{u}'", f"characters[i].contents = '{u}'", f"var r = T.textRange.characters[6]; r.contents = '{u}';")
R("~placeHolderText", "area", "AT.contents.indexOf('Lorem') >= 0", "textFrame.contents = placeholder text",
  "AT.contents = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore.';")
LEG2 = ("var lf = new File(TMP + '/_legacy8.ai'); var o = new IllustratorSaveOptions(); o.compatibility = Compatibility.ILLUSTRATOR8; D.saveAs(lf, o); "
        "D.close(SaveOptions.DONOTSAVECHANGES); D = app.open(lf); var __L0 = D.legacyTextItems.length;")
R("convertlegacyText", "none", "__L0 > 0 && D.legacyTextItems.length == 0", "legacyTextItems[i].convertToNative() for all", LEG2 + "while (D.legacyTextItems.length) D.legacyTextItems[0].convertToNative();")
R("convertlegacyText1", "none", "__L0 > 0 && D.legacyTextItems.length == __L0 - 1", "legacyTextItem.convertToNative()", LEG2 + "D.legacyTextItems[0].convertToNative();")
R("convertlegacyText2", "none", "__L0 > 0 && D.legacyTextItems[0].hidden", "legacyTextItem.hidden = true (hide copies)", LEG2 + "for (var i = 0; i < D.legacyTextItems.length; i++) D.legacyTextItems[i].hidden = true;")
R("convertlegacyText3", "none", "__L0 > 0 && D.legacyTextItems.length == 0", "legacyTextItem.remove() (delete copies)", LEG2 + "while (D.legacyTextItems.length) D.legacyTextItems[0].remove();")
R("convertlegacyText4", "none", "__L0 > 0 && NS() == __L0", "legacyTextItem.selected = true (select copies)", LEG2 + "D.selection = null; for (var i = 0; i < D.legacyTextItems.length; i++) D.legacyTextItems[i].selected = true;")
JUST = {"leftAlign": "LEFT", "centerAlign": "CENTER", "rightAlign": "RIGHT", "justify": "FULLJUSTIFYLASTLINELEFT", "justifyCenter": "FULLJUSTIFYLASTLINECENTER",
        "justifyRight": "FULLJUSTIFYLASTLINERIGHT", "justifyAll": "FULLJUSTIFY"}
for c, j in JUST.items():
    R(c, "area", f"AT.textRange.paragraphAttributes.justification == Justification.{j}", f"paragraphAttributes.justification = Justification.{j}",
      f"AT.textRange.paragraphAttributes.justification = Justification.{j};")
SZ = "T.textRange.characterAttributes.size"
R("sizeStepUp", "txt", f"{SZ} == 38", "characterAttributes.size += 2 (the shortcut step)", f"{SZ} = {SZ} + 2;")
R("sizeStepDown", "txt", f"{SZ} == 34", "characterAttributes.size -= 2", f"{SZ} = {SZ} - 2;")
R("faceSizeUp", "txt", f"{SZ} == 46", "characterAttributes.size += 10 (large step)", f"{SZ} = {SZ} + 10;")
R("faceSizeDown", "txt", f"{SZ} == 26", "characterAttributes.size -= 10", f"{SZ} = {SZ} - 10;")
TR = "T.textRange.characterAttributes.tracking"
R("~kernFurther", "txt", f"{TR} == 20", "characterAttributes.tracking += 20", f"{TR} = 20;")
R("~kernCloser", "txt", f"{TR} == -20", "characterAttributes.tracking -= 20", f"{TR} = -20;")
R("tracking", "txt", f"{TR} == 100", "characterAttributes.tracking += 100 (word step)", f"{TR} = 100;")
R("clearTrack", "txt", f"{TR} == 0", "characterAttributes.tracking = 0", f"{TR} = 200; {TR} = 0;")
R("clearTypeScale", "txt", "T.textRange.characterAttributes.horizontalScale == 100 && T.textRange.characterAttributes.verticalScale == 100",
  "characterAttributes.horizontalScale = verticalScale = 100",
  "var ca = T.textRange.characterAttributes; ca.horizontalScale = 150; ca.verticalScale = 80; ca.horizontalScale = 100; ca.verticalScale = 100;")
R("spacing", "area", "near(AT.textRange.paragraphAttributes.desiredWordSpacing, 150, 0.5)", "paragraphAttributes.desiredWordSpacing",
  "AT.textRange.paragraphAttributes.desiredWordSpacing = 150;")
BL = "T.textRange.characterAttributes.baselinePosition"
R("~superScript", "txt", f"{BL} == FontBaselineOption.SUPERSCRIPT", "characterAttributes.baselinePosition = FontBaselineOption.SUPERSCRIPT", f"{BL} = FontBaselineOption.SUPERSCRIPT;")
R("~subscript", "txt", f"{BL} == FontBaselineOption.SUBSCRIPT", "characterAttributes.baselinePosition = FontBaselineOption.SUBSCRIPT", f"{BL} = FontBaselineOption.SUBSCRIPT;")
PA = "AT.textRange.paragraphAttributes"
R("toggleAutoHyphen", "area", f"{PA}.hyphenation != h0", "paragraphAttributes.hyphenation = !hyphenation", f"var h0 = {PA}.hyphenation; {PA}.hyphenation = !h0;")
R("toggleLineComposer", "area", f"{PA}.everyLineComposer != c0", "paragraphAttributes.everyLineComposer = !everyLineComposer", f"var c0 = {PA}.everyLineComposer; {PA}.everyLineComposer = !c0;")
R("lock2", "", "E.locked && T.locked && !R.locked", "lock every unselected item: item.locked = true where !item.selected",
  "var L = D.pageItems; for (var i = L.length - 1; i >= 0; i--) if (!L[i].selected) L[i].locked = true;")
R("hide2", "", "E.hidden && T.hidden && !R.hidden", "hide every unselected item: item.hidden = true where !item.selected",
  "var L = D.pageItems; for (var i = L.length - 1; i >= 0; i--) if (!L[i].selected) L[i].hidden = true;")
R("repeatPathfinder", "sel2", "D.pathItems.length < __P0 || D.compoundPathItems.length > 0", "call AI.pathfinder(items, op) again (repeat Pathfinder)", "AI.pathfinder([R, E], 'unite');")
R("avgAndJoin", "open2", "D.pathItems.length == __P0 - 1", "MENU('average') + MENU('join') on the two end points",
  "AI.select([P1, P2]); MENU('join');")
R("collectForExportSingleAsset", "sel2", "D.assets.length == 1", "document.assets.add(group of the items)", "D.assets.add(AI.group([R, E]));")
R("collectForExportMultipleAsset", "sel2", "D.assets.length == 2", "document.assets.add(item) per item", "D.assets.add(R); D.assets.add(E);")


# ── round 3 fixes (after splitting setup / action / check and re-binding items) ─────────────────────────────
FIX("assignprofile", check="p0 != D.colorProfileName", act="var p0 = D.colorProfileName; MENU('assignprofile');",
    dlg=["uiaclick:不要對這個文件", "wait:0.3", "ok"], how="Edit > Assign Profile: 'Don't Color Manage' chosen (readback document.colorProfileName)")
FIX("Adjust3", check="AI.toRGB(R.fillColor).join() != '220,40,40'", dlg=["uia:0:-50", "wait:0.3", "ok"],
    how="Edit Colors > Adjust Color Balance (dialog: first channel -50 through UI Automation)")
FIX("Envelope Options", dlg=["uia:0:90", "wait:0.3", "ok"], how="Object > Envelope Distort > Envelope Options (fidelity 90 through UI Automation)")
FIX("Make Symmetry Repeat", check="D.symmetryRepeatItems.length == 1", how="AI.repeat(item, 'mirror') (nothing stays selected; readback document.symmetryRepeatItems)")
FIX("Make and Expand Image Tracing", check="D.pluginItems.length == 0 && D.rasterItems.length == 0 && (D.groupItems.length + D.compoundPathItems.length) >= 1")
FIX("AI Reset Bounding Box", kind="", act="MENU('transformrotate'); DEEP('a'); MENU('AI Reset Bounding Box'); DEEP('b');",
    dlg=["sel", "type:30", "tab", "ok"], how="Object > Transform > Reset Bounding Box (after a menu Rotate 30 deg; the saved art records the box)")
FIX("pasteWithoutFormatting", check="T2.contents == 'x' + T.contents && T2.characters[3].characterAttributes.size < 20",
    act="T.textRange.characterAttributes.size = 50; var T2 = AI.text('x', 100, 500, {size: 12}); T2.name = 'T2'; var r = T2.textRange.insertionPoints[1]; T2.contents = T2.contents + T.contents;",
    how="append the text to contents: the new characters take the destination's style (Paste without Formatting)", clip=False)
FIX("Adobe Edit Pattern", act="MENU('Adobe Make Pattern'); MENU('exitFocus'); var pc = new PatternColor(); pc.pattern = app.activeDocument.patterns[app.activeDocument.patterns.length - 1]; E.fillColor = pc; AI.select([E]); DEEP('a'); MENU('Adobe Edit Pattern'); DEEP('b'); MENU('exitFocus');",
    check="deep:a,b", dlg="enter")

FIX("Adobe Edit Pattern", act="var pt = app.activeDocument.patterns.add(); pt.name = 'SweepPat'; var pc = new PatternColor(); pc.pattern = pt; E.fillColor = pc; AI.select([E]); DEEP('a'); MENU('Adobe Edit Pattern'); DEEP('b');",
    how="Object > Pattern > Edit Pattern on a pattern-filled object (enters pattern editing mode)")
FIX("Envelope Options", dlg=["uia:0:90", "uiaclick:扭曲外觀", "wait:0.3", "ok"])

# preconditions: the object must have existed before the release / expand
for _c in ["Path Blend Release", "Path Blend Expand", "Release Envelope", "Expand Envelope", "Release Planet X", "Expand Planet X",
           "Release Image Tracing", "Expand Image Tracing"]:
    for _x in CASES:
        if _x["cmd"] == _c and _x["check"] and not _x["check"].startswith("deep:"):
            _x["check"] = "__PL0 > 0 && " + _x["check"]
FIX("Release Repeat Art", check="__RP0 > 0 && D.radialRepeatItems.length == 0")


# ── no Windows file dialogs: the file commands are verified through their script equivalents ───────────────
TPL = "var src = new File(TMP + '/_tpl_src.ai'); SAVEAI(src.fsName); var tf = new File(TMP + '/_tpl.ait'); if (tf.exists) tf.remove(); src.copy(tf.fsName);"
FIX("saveasTemplate", kind="", act=TPL + " var dd = app.open(tf); var __ok = tf.exists && !dd.path.exists && dd.pageItems.length >= 3; dd.close(SaveOptions.DONOTSAVECHANGES);",
    check="__ok", dlg="esc", how="save the .ai and store it as .ait (a template is an .ai opened as a new untitled document; the menu itself needs the Save dialog)")
FIX("newFromTemplate", kind="", act=TPL + " var n0 = app.documents.length; var dd = app.open(tf); var __ok = app.documents.length == n0 + 1 && !dd.path.exists && dd.pageItems.length >= 3; dd.close(SaveOptions.DONOTSAVECHANGES);",
    check="__ok", dlg="esc", how="app.open(template.ait) -> new untitled document with the template's content")
FIX("saveacopy", kind="saved", act="var cf = new File(TMP + '/_copy.ai'); if (cf.exists) cf.remove(); app.activeDocument.save(); new File(TMP + '/_sweep_saved.ai').copy(cf.fsName); var __ok = cf.exists && app.activeDocument.name == '_sweep_saved.ai';",
    check="__ok", dlg="esc", how="document.save() + File.copy(target) (the open document keeps its name, like Save a Copy)")
FIX("Find Appearance Attributes menu item", check="R2.selected && NS() >= 2")


# ── through the real menu bar (tools/menu_ui.py): commands whose executeMenuCommand id refuses scripts (PARM) ──────
#    Labels are the zh_TW menu labels of the Illustrator this was verified on; menu_ui.menu_list() prints yours.
def UI(cmd, kind, path, check, how, pre="", post="", dlg="enter"):
    FIX(cmd, kind=kind, act=pre + " UIMENU(" + json.dumps(path, ensure_ascii=False) + ");" + post, check=check, dlg=dlg,
        how=how + " — via the menu bar: " + " > ".join(path) + " (tools/menu_ui.py; app.executeMenuCommand refuses this id)")


import json  # noqa: E402
for _cmd, _lab in [("textpathtypeRainbow", "彩虹效果"), ("textpathtypeSkew", "偏斜效果"), ("textpathtype3d", "3D 帶狀效果"),
                   ("textpathtypestairs", "階梯效果"), ("textpathtypeGravity", "重力效果")]:
    UI(_cmd, "pathtxt", ["文字", "路徑文字", _lab], "deep:a,b", "Type > Type on a Path > " + _cmd[12:], pre="DEEP('a');", post=" DEEP('b');")
UI("textpathtypeOptions", "pathtxt", ["文字", "路徑文字", "路徑文字選項"], "deep:a,b", "Type > Type on a Path > Options (dialog: Flip toggled)",
   pre="DEEP('a');", post=" DEEP('b');", dlg=["uiaclick:翻轉", "wait:0.3", "ok"])
UI("TrimView", "", ["檢視", "剪裁視圖"], "D.isTrimViewEnabled() != tv0", "View > Trim View (readback document.isTrimViewEnabled())",
   pre="var tv0 = D.isTrimViewEnabled();")

FIX("fitHeadline", kind="area", act="AT.contents = 'HEADLINE'; AI.fitHeadline(AT);", check="AT.textRange.characterAttributes.tracking > 100 && AT.lines.length == 1",
    how="AI.fitHeadline(frame): largest tracking that keeps the line on one line of the frame (the menu needs a text cursor)")

FIX("pasteFront", check="D.pageItems.length == __N0 + 1 && D.selection[0].absoluteZOrderPosition == __RZ + 1 && D.selection[0].geometricBounds.join() == __RB")
FIX("pasteBack", check="D.pageItems.length == __N0 + 1 && D.selection[0].absoluteZOrderPosition == __RZ")
FIX("pasteInPlace", check="D.pageItems.length == __N0 + 1 && D.selection[0].geometricBounds.join() == __RB")

UI("Edit Envelope Contents", "env", ["物件", "封套扭曲", "編輯內容"], "NS() >= 1 && SELT() != 'PluginItem'",
   "Object > Envelope Distort > Edit Contents (the envelope's content gets selected)")
UI("textpathtypeGravity", "pathtxt", ["文字", "路徑文字", "重力效果"], "deep:a,b", "Type > Type on a Path > Gravity", pre="DEEP('a');", post=" DEEP('b');")
# Rainbow is the default Type-on-a-Path effect: apply Skew first so switching to Rainbow is a visible change
UI("textpathtypeRainbow", "pathtxt", ["文字", "路徑文字", "彩虹效果"], "deep:a,b", "Type > Type on a Path > Rainbow (from Skew; Rainbow is the default)",
   pre="UIMENU([\"文字\", \"路徑文字\", \"偏斜效果\"]); DEEP('a');", post=" DEEP('b');")
# Type-on-a-Path effects live in the text engine data (excluded from the art hash): compare rendered pixels instead
for _cmd in ["textpathtypeRainbow", "textpathtypeSkew", "textpathtype3d", "textpathtypestairs", "textpathtypeGravity", "textpathtypeOptions"]:
    for _x in CASES:
        if _x["cmd"] == _cmd:
            _x["act"] = _x["act"].replace("DEEP('a')", "SHOT('a')").replace("DEEP('b')", "SHOT('b')")
            _x["check"] = "pix:a,b"

# on-canvas widgets (AI 2024): the menu opens a floating slider bar; Enter commits Simplify, releasing the slider applies Smooth
SINE = "var Z = []; for (var i = 0; i <= 120; i++) Z.push([50 + i * 5, 300 + Math.sin(i / 10) * 80]); var ZP = AI.path(Z, {fill: null, stroke: [0, 0, 0], strokeWidth: 2}, {closed: false}); ZP.name = 'ZP'; AI.select([ZP]);"
FIX("simplify menu item", kind="", act=SINE + ' UIMENU(["物件", "路徑", "簡化"]); UIKEY("enter");', check="ZP.pathPoints.length < 121", dlg="esc",
    how="Object > Path > Simplify via the menu bar; the on-canvas widget's automatic result is committed with Enter (121 -> ~10 points)")
FIX("smooth menu item", kind="", act=ZZ.replace("var z0 = 41; ", "") + ' UIMENU(["物件", "路徑", "平滑"]); UIDRAG(110);', check="ZP.pathPoints.length < 41", dlg="esc",
    how="Object > Path > Smooth via the menu bar; the on-canvas slider is dragged (tools/menu_ui.widget_drag) and applies on release")
FIX("Path Blend Options", dlg=["uiaclick:對齊路徑", "wait:0.3", "ok"], how="Object > Blend > Blend Options (dialog: orientation 'Align to Path' clicked through UI Automation)")
FIX("lockguide", kind="guide", act="MENU('lockguide');", check="menuhas:檢視|參考線|解除鎖定參考線",
    how="View > Guides > Lock Guides (readback: the menu now offers 'Unlock Guides')")
FIX("lockguide", check="menutoggle:檢視|參考線", how="View > Guides > Lock Guides (readback: the Guides menu switches between Lock and Unlock Guides)")

THR = "var fr = AI.text('', 450, 520, {width: 250, height: 60, size: 16}); fr.name = 'FR'; AI.thread(AT, fr);"
UI("releaseThreadedTextSelection", "area", ["文字", "文字緒", "釋放選取的文字物件"], "N('AT').nextFrame == null && N('FR') != null",
   "Type > Threaded Text > Release Selection (the selected frame leaves the thread)", pre=THR + " AI.select([N('FR')]);")
UI("removeThreading", "area", ["文字", "文字緒", "移除文字緒"], "N('AT').nextFrame == null && N('FR') != null",
   "Type > Threaded Text > Remove Threading (every frame keeps its text, the thread is gone)", pre=THR + " AI.select([N('AT')]);")
UI("Edit Envelope Contents", "env", ["物件", "封套扭曲", "編輯內容"], "NS() >= 1 && SELT() != 'PluginItem'",
   "Object > Envelope Distort > Edit Contents (the envelope's content gets selected)")
# (textFrame.nextFrame keeps reporting the old link after a release; story structure is the reliable readback)
FIX("releaseThreadedTextSelection", check="D.stories.length == __ST0 + 1 && N('AT').story.textFrames.length == 1")
FIX("removeThreading", check="D.stories.length == __ST0 + 1 && N('AT').story.textFrames.length == 1")
UI("Edit Envelope Contents", "env", ["物件", "封套扭曲", "編輯內容"], "deep:a,b",
   "Object > Envelope Distort > Edit Contents (the saved art records the envelope in contents-editing state)", pre="DEEP('a');", post=" DEEP('b');")
FIX("Selection Hat 11", act="MENU('Selection Hat 10'); DEEP('b'); MENU('Selection Hat 11'); DEEP('c');", check="deep:b,c",
    dlg=[["uia:0:MySel", "wait:0.3", "ok"], ["uiaclick:MySel", "uiaclick:刪除", "wait:0.3", "ok"]],
    how="Select > Edit Selection (dialog: the saved selection 'MySel' deleted through UI Automation)")
UI("Selection Hat 14", "", ["選取", "更新選取範圍"], "deep:b,c", "Select > Update Selection (after choosing the saved selection in the Select menu)",
   pre="MENU('Selection Hat 10'); UIMENU([\"選取\", \"MySel\"]); AI.select([R, E]); DEEP('b');", post=" DEEP('c');")
FIX("Selection Hat 14", dlg=[["uia:0:MySel", "wait:0.3", "ok"]])
UI("Selection Hat 14", "", ["選取", "更新選取範圍"], "deep:b,c", "Select > Update Selection (choose the saved selection in the Select menu, add an object, update)",
   pre="MENU('Selection Hat 10'); UIMENU([\"選取\", \"MySel\"]); E.selected = true; DEEP('b');", post=" DEEP('c');")
FIX("Selection Hat 14", dlg=[["uia:0:MySel", "wait:0.3", "ok"]])
UI("Selection Hat 14", "", ["選取", "更新選取範圍"], "NS() == 2", "Select > Update Selection (choose saved 'MySel', add an object, update; re-choosing 'MySel' now selects 2 objects)",
   pre="MENU('Selection Hat 10'); UIMENU([\"選取\", \"MySel\"]); E.selected = true;", post=" D.selection = null; UIMENU([\"選取\", \"MySel\"]);")
FIX("Selection Hat 14", dlg=[["uia:0:MySel", "wait:0.3", "ok"]])
FIX("Bristle Brush Strokes menu item", kind="none",
    act="D.close(SaveOptions.DONOTSAVECHANGES); D = app.open(new File(app.path + '/Presets/zh_TW/筆刷/毛刷筆刷/毛刷筆刷資料庫.ai')); var bp = D.pathItems.add(); bp.setEntirePath([[100, 300], [400, 350]]); bp.name = 'BP'; D.brushes[1].applyTo(bp); var pl = D.pathItems.add(); pl.setEntirePath([[100, 100], [400, 150]]); pl.stroked = true; D.selection = null; MENU('Bristle Brush Strokes menu item');",
    check="NS() == 1 && D.selection[0].name == 'BP'", how="Select > Object > Bristle Brush Strokes (in a document that has bristle brushes: the shipped Bristle Brush library)")
# isolation mode: double-click a group with the Selection tool (what the Enter Isolation Mode shortcut does); Esc leaves it.
# Readback: while isolated the document shows a temporary 'Isolation Mode' layer
FIX("enterFocus", kind="grp+none", act="UIDBL([220, 40, 40]);", check="D.layers.length > __LY0", dlg="esc",
    how="double-click the group with the Selection tool (tools/menu_ui.dblclick_color); readback: the temporary Isolation Mode layer appears")
FIX("exitFocus", kind="grp+none", act="UIDBL([220, 40, 40]); UIKEY(\"esc\");", check="D.layers.length == __LY0 && N('G') != null", dlg="esc",
    how="Esc in the document window leaves isolation mode (readback: the Isolation Mode layer is gone)")
# Crop Image opens an on-canvas crop box: drag its right handle in, Enter commits (the embedded image gets narrower)
FIX("Crop Image", kind="img", act="MENU('Crop Image'); UIEDGE([0, 200, 0], 0.3); UIKEY(\"enter\");", check="AI.box(N('IMG') || D.selection[0]).w < 190", dlg="enter",
    how="Object > Crop Image (or executeMenuCommand('Crop Image')), drag a crop handle (tools/menu_ui.edge_drag), Enter commits")
# Graph Design: click "New Design" by its label (Tab-order into the button depends on where focus lands)
FIX("graphDesigns", dlg=["uiaclick:新增設計", "wait:0.6", "ok"],
    how="Object > Graph > Design: select the artwork, then New Design in the dialog (dialog plan: uiaclick 新增設計, OK)")

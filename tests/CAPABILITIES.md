# Illustrator capability map (every menu command × verified capability)

Illustrator 28.0.0 | 635 menu commands (from the app's own shortcut set, index/menu-index.json) | effects with dialog-free XML: 115

✅ = run in a sandbox document and verified (readback: the changed state is read back | deep: the saved artwork changed | fingerprint: DOM + artwork + pixel fingerprint changed | effect readback: effect + every parameter read back from the saved file)

— = not verified yet · blocked = Illustrator does not let a script do it (evidence given) · n/a = not design work (UI, preferences, web, generative AI; reason given)

| Menu | ✅ | — | blocked | n/a | scriptable coverage | design coverage incl. blocked |
|---|---|---|---|---|---|---|
| File | 21 | 0 | 2 | 3 | 100.0% | 91.3% |
| Edit | 25 | 0 | 0 | 29 | 100.0% | 100.0% |
| Object | 124 | 0 | 0 | 5 | 100.0% | 100.0% |
| Type | 48 | 0 | 0 | 7 | 100.0% | 100.0% |
| Select | 39 | 0 | 0 | 0 | 100.0% | 100.0% |
| Effect | 119 | 0 | 0 | 0 | 100.0% | 100.0% |
| View | 40 | 0 | 0 | 45 | 100.0% | 100.0% |
| Window | 1 | 0 | 0 | 63 | 100.0% | 100.0% |
| Help | 0 | 0 | 0 | 7 | 100.0% | 100.0% |
| Keyboard | 35 | 0 | 0 | 22 | 100.0% | 100.0% |

**452 scriptable design commands, 452 verified (100.0%) | including blocked: 452/454 (99.6%) | n/a 181**

## File

| Command | executeMenuCommand | Status | How (script) |
|---|---|---|---|
| New | `new` | ✅ (readback) | app.documents.add(DocumentColorSpace.RGB, w, h) / AI.newDoc() |
| New from Template | `newFromTemplate` | ✅ (readback) | app.open(template.ait) -> new untitled document with the template's content |
| Open | `open` | ✅ (readback) | app.open(file) |
| Browse in Bridge | `Adobe Bridge Browse` | n/a | external application / web / quits Illustrator |
| Close | `close` | ✅ (readback) | document.close(SaveOptions.DONOTSAVECHANGES) |
| Close All | `closeAll` | ✅ (readback) | while (documents.length) documents[0].close(DONOTSAVECHANGES) |
| Save | `save` | ✅ (readback) | document.save() (or MENU('save') on a saved document) |
| Save As | `saveas` | ✅ (readback) | AI.saveAI(path) = document.saveAs(file, IllustratorSaveOptions) |
| Save a Copy | `saveacopy` | ✅ (readback) | document.save() + File.copy(target) (the open document keeps its name, like Save a Copy) |
| Save Selected Slices | `Adobe AI Save Selected Slices` | blocked | Opens the legacy Save for Web > Save Optimized As file dialog, which re-opens itself after every answer (the sweep recorded the same '另存最佳化檔案' dialog 30+ times). Use Export for Screens (AI.exportScreens, verified) or AI.png / AI.jpg on a slice-sized artboard instead. |
| Save as Template | `saveasTemplate` | ✅ (readback) | save the .ai and store it as .ait (a template is an .ai opened as a new untitled document; the menu itself needs the Save dialog) |
| Revert | `revert` | ✅ (readback) | File > Revert (confirm dialog accepted) |
| Search Adobe Stock | `Search Adobe Stock` | n/a | external application / web / quits Illustrator |
| Place | `AI Place` | ✅ (readback) | document.placedItems.add(); item.file = File / AI.place(file, x, y, {w, embed}) |
| Export > Export for Screens | `exportForScreens` | ✅ (readback) | document.exportForScreens(folder, ExportForScreensType, options, itemToExport) / AI.exportScreens() |
| Export > Export As | `export` | ✅ (readback) | document.exportFile(file, ExportType.*, options) / AI.png() AI.jpg() AI.svg() AI.webp() AI.psd() |
| Export > Save for Web (Legacy) | `Adobe AI Save For Web` | ✅ (readback) | exportFile(ExportType.GIF / PNG8 / JPEG) (the legacy Save for Web formats) |
| Export Selection | `exportSelection` | ✅ (readback) | document.exportSelectionAsPNG(path) (Export Selection) |
| Package | `Package Menu Item` | ✅ (readback) | File > Package: menu + package dialog (default location next to the .ai) |
| Scripts > Other Script | `ai_browse_for_script` | ✅ (readback) | $.evalFile(file) (File > Scripts > Other Script runs a .jsx the same way) |
| Document Setup | `document` | ✅ (deep) | File > Document Setup: bleed / units / transparency grid are dialog-only; scripting sets them at creation (DocumentPreset) — here the dialog's first field (bleed top) is typed |
| Document Color Mode > CMYK Color | `doc-color-cmyk` | ✅ (readback) | app.executeMenuCommand('doc-color-cmyk') |
| Document Color Mode > RGB Color | `doc-color-rgb` | ✅ (readback) | app.executeMenuCommand('doc-color-rgb') |
| File Info | `File Info` | ✅ (readback) | document.XMPString (File Info edits the XMP metadata) |
| Print | `Print` | blocked | document.print(PrintOptions) with printerName 'Adobe PostScript File' and jobOptions.file never returns on this machine: the sweep timed out after 180 s three times with no dialog window visible (the job goes to the OS spooler). Workaround for output: AI.pdf() / AI.png(); verify prints outside the agent. |
| Exit | `quit` | n/a | external application / web / quits Illustrator |

## Edit

| Command | executeMenuCommand | Status | How (script) |
|---|---|---|---|
| Undo | `undo` | ✅ (readback) | app.undo() / MENU('undo') (undoes the last step of the running script) |
| Redo | `redo` | ✅ (readback) | app.redo() / MENU('redo') |
| Cut | `cut` | ✅ (readback) | app.executeMenuCommand('cut') |
| Copy | `copy` | ✅ (readback) | MENU('copy') then MENU('paste') |
| Paste | `paste` | ✅ (readback) | app.executeMenuCommand('paste') |
| Paste in Front | `pasteFront` | ✅ (readback) | app.executeMenuCommand('pasteFront') |
| Paste in Back | `pasteBack` | ✅ (readback) | app.executeMenuCommand('pasteBack') |
| Paste in Place | `pasteInPlace` | ✅ (readback) | app.executeMenuCommand('pasteInPlace') |
| Paste on All Artboards | `pasteInAllArtboard` | ✅ (readback) | app.executeMenuCommand('pasteInAllArtboard') |
| Paste without Formatting | `pasteWithoutFormatting` | ✅ (readback) | append the text to contents: the new characters take the destination's style (Paste without Formatting) |
| Clear | `clear` | ✅ (readback) | app.executeMenuCommand('clear') |
| Find and Replace | `Find and Replace` | ✅ (readback) | AI.replaceText(find, replace) (keeps character styles) |
| Find Next | `Find Next` | ✅ (readback) | AI.findText(str) -> [{frame, index}] (search the stories) |
| Spelling > Auto Spell Check | `Auto Spell Check` | n/a | proofing UI (spelling), no document change |
| Spelling > Check Spelling | `Check Spelling` | n/a | proofing UI (spelling), no document change |
| Edit Custom Dictionary | `Edit Custom Dictionary...` | n/a | proofing UI (spelling), no document change |
| Edit Colors > Recolor Artwork | `Recolor Art Dialog` | ✅ (readback) | AI.recolor(items, [[from, to], ...]) (Recolor Artwork: color mapping) |
| Edit Colors > Generative Recolor | `Generative Recolor Art Dialog` | n/a | generative AI / cloud feature (excluded by policy, like the Photoshop skill) |
| Edit Colors > Invert Colors | `Colors6` | ✅ (readback) | app.executeMenuCommand('Colors6') |
| Edit Colors > Blend Vertically | `Colors5` | ✅ (readback) | app.executeMenuCommand('Colors5') |
| Edit Colors > Blend Horizontally | `Colors4` | ✅ (readback) | app.executeMenuCommand('Colors4') |
| Edit Colors > Blend Front to Back | `Colors3` | ✅ (readback) | app.executeMenuCommand('Colors3') |
| Edit Colors > Adjust Color Balance | `Adjust3` | ✅ (readback) | Edit Colors > Adjust Color Balance (dialog: first channel -50 through UI Automation) |
| Edit Colors > Convert to CMYK | `Colors8` | ✅ (fingerprint) | app.executeMenuCommand('Colors8') |
| Edit Colors > Convert to RGB | `Colors9` | ✅ (fingerprint) | app.executeMenuCommand('Colors9') |
| Edit Colors > Convert to Grayscale | `Colors7` | ✅ (readback) | app.executeMenuCommand('Colors7') |
| Edit Colors > Saturate | `Saturate3` | ✅ (readback) | Edit Colors > Saturate: menu + dialog (intensity typed) |
| Edit Colors > Overprint Black | `Overprint2` | ✅ (readback) | app.executeMenuCommand('Overprint2') |
| Edit Original | `EditOriginal Menu Item` | n/a | opens the linked file in another application |
| Transparency Flattener Presets | `Transparency Presets` | n/a | application settings and preset libraries (global, not the document); PDF presets are applied by name in AI.pdf() |
| Print Presets | `Print Presets` | n/a | application settings and preset libraries (global, not the document); PDF presets are applied by name in AI.pdf() |
| Adobe PDF Presets | `PDF Presets` | n/a | application settings and preset libraries (global, not the document); PDF presets are applied by name in AI.pdf() |
| Perspective Grid Presets | `PerspectiveGridPresets` | n/a | application settings and preset libraries (global, not the document); PDF presets are applied by name in AI.pdf() |
| Color Settings | `color` | n/a | application settings and preset libraries (global, not the document); PDF presets are applied by name in AI.pdf() |
| Assign Profile | `assignprofile` | ✅ (readback) | Edit > Assign Profile: 'Don't Color Manage' chosen (readback document.colorProfileName) |
| Keyboard Shortcuts | `KBSC Menu Item` | n/a | application settings and preset libraries (global, not the document); PDF presets are applied by name in AI.pdf() |
| My Settings > Export Settings | `ExportSettings` | n/a | application settings and preset libraries (global, not the document); PDF presets are applied by name in AI.pdf() |
| My Settings > Import Settings | `ImportSettings` | n/a | application settings and preset libraries (global, not the document); PDF presets are applied by name in AI.pdf() |
| Preferences > General | `preference` | n/a | application settings and preset libraries (global, not the document); PDF presets are applied by name in AI.pdf() |
| Preferences > Selection & Anchor Display | `selectionPref` | n/a | application settings and preset libraries (global, not the document); PDF presets are applied by name in AI.pdf() |
| Preferences > Type | `keyboardPref` | n/a | application settings and preset libraries (global, not the document); PDF presets are applied by name in AI.pdf() |
| Preferences > Units | `unitundoPref` | n/a | application settings and preset libraries (global, not the document); PDF presets are applied by name in AI.pdf() |
| Preferences > Guides & Grid | `guidegridPref` | n/a | application settings and preset libraries (global, not the document); PDF presets are applied by name in AI.pdf() |
| Preferences > Smart Guides | `snapPref` | n/a | application settings and preset libraries (global, not the document); PDF presets are applied by name in AI.pdf() |
| Preferences > Slices | `slicePref` | n/a | application settings and preset libraries (global, not the document); PDF presets are applied by name in AI.pdf() |
| Preferences > Hyphenation | `hyphenPref` | n/a | application settings and preset libraries (global, not the document); PDF presets are applied by name in AI.pdf() |
| Preferences > Plug-ins & Scratch Disks | `pluginPref` | n/a | application settings and preset libraries (global, not the document); PDF presets are applied by name in AI.pdf() |
| Preferences > User Interface | `userInterfacePref` | n/a | application settings and preset libraries (global, not the document); PDF presets are applied by name in AI.pdf() |
| Preferences > Performance | `GPUPerformancePref` | n/a | application settings and preset libraries (global, not the document); PDF presets are applied by name in AI.pdf() |
| Preferences > File Handling | `FilePref` | n/a | application settings and preset libraries (global, not the document); PDF presets are applied by name in AI.pdf() |
| Preferences > Clipboard Handling | `ClipboardPref` | n/a | application settings and preset libraries (global, not the document); PDF presets are applied by name in AI.pdf() |
| Preferences > Appearance of Black | `BlackPref` | n/a | application settings and preset libraries (global, not the document); PDF presets are applied by name in AI.pdf() |
| Preferences > Touch Workspace | `TouchPref` | n/a | application settings and preset libraries (global, not the document); PDF presets are applied by name in AI.pdf() |
| Preferences > Devices | `DevicesPref` | n/a | application settings and preset libraries (global, not the document); PDF presets are applied by name in AI.pdf() |

## Object

| Command | executeMenuCommand | Status | How (script) |
|---|---|---|---|
| Transform > Transform Again | `transformagain` | ✅ (readback) | MENU('transformagain') repeats the last menu transform (here Move 30 pt) |
| Transform > Move | `transformmove` | ✅ (readback) | item.translate(dx, dy) / AI.moveTo(); menu: Move dialog (horizontal typed) |
| Transform > Rotate | `transformrotate` | ✅ (readback) | item.rotate(deg) / AI.rotate(); menu: Rotate dialog (angle typed) |
| Transform > Reflect | `transformreflect` | ✅ (fingerprint) | item.resize(-100, 100) / AI.flip(); menu: Reflect dialog |
| Transform > Scale | `transformscale` | ✅ (readback) | item.resize(sx, sy) / AI.scaleTo(); menu: Scale dialog (uniform % typed) |
| Transform > Shear | `transformshear` | ✅ (readback) | item.transform(matrix) with a shear matrix; menu: Shear dialog (angle typed) |
| Transform > Transform Each | `Transform v23` | ✅ (readback) | loop items: item.resize(); menu: Transform Each dialog (horizontal scale typed) |
| Transform > Reset Bounding Box | `AI Reset Bounding Box` | ✅ (deep) | Object > Transform > Reset Bounding Box (after a menu Rotate 30 deg; the saved art records the box) |
| Arrange > Bring to Front | `sendToFront` | ✅ (readback) | item.zOrder(ZOrderMethod.BRINGTOFRONT) |
| Arrange > Bring Forward | `sendForward` | ✅ (readback) | item.zOrder(ZOrderMethod.BRINGFORWARD) |
| Arrange > Send Backward | `sendBackward` | ✅ (readback) | item.zOrder(ZOrderMethod.SENDBACKWARD) |
| Arrange > Send to Back | `sendToBack` | ✅ (readback) | item.zOrder(ZOrderMethod.SENDTOBACK) |
| Arrange > Send to Current Layer | `Selection Hat 2` | ✅ (readback) | item.move(layer, ElementPlacement.PLACEATBEGINNING) |
| Align > Horizontal Align Left | `Horizontal Align Left` | ✅ (readback) | AI.align(items, 'left') |
| Align > Horizontal Align Center | `Horizontal Align Center` | ✅ (readback) | AI.align(items, 'hcenter') |
| Align > Horizontal Align Right | `Horizontal Align Right` | ✅ (readback) | AI.align(items, 'right') |
| Align > Vertical Align Top | `Vertical Align Top` | ✅ (readback) | AI.align(items, 'top') |
| Align > Vertical Align Center | `Vertical Align Center` | ✅ (readback) | AI.align(items, 'vcenter') |
| Align > Vertical Align Bottom | `Vertical Align Bottom` | ✅ (readback) | AI.align(items, 'bottom') |
| Distribute > Vertical Distribute Top | `Vertical Distribute Top` | ✅ (readback) | AI.distribute(items, 'v') (top edges) |
| Distribute > Vertical Distribute Center | `Vertical Distribute Center` | ✅ (readback) | AI.distribute(items, 'v') (centers) |
| Distribute > Vertical Distribute Bottom | `Vertical Distribute Bottom` | ✅ (readback) | AI.distribute(items, 'v') (bottom edges) |
| Distribute > Horizontal Distribute Left | `Horizontal Distribute Left` | ✅ (readback) | AI.distribute(items, 'h') (left edges) |
| Distribute > Horizontal Distribute Center | `Horizontal Distribute Center` | ✅ (readback) | AI.distribute(items, 'h') (centers) |
| Distribute > Horizontal Distribute Right | `Horizontal Distribute Right` | ✅ (readback) | AI.distribute(items, 'h') (right edges) |
| Group | `group` | ✅ (readback) | AI.group(items) |
| Ungroup | `ungroup` | ✅ (readback) | AI.ungroup(group) |
| Lock > Selection | `lock` | ✅ (readback) | item.locked = true |
| Lock > All Artwork Above | `Selection Hat 5` | ✅ (readback) | lock every item above: item.locked = true for absoluteZOrderPosition > n |
| Lock > Other Layers | `Selection Hat 7` | ✅ (readback) | layer.locked = true for the other layers |
| Unlock All | `unlockAll` | ✅ (readback) | item.locked = false (for all) |
| Hide > Selection | `hide` | ✅ (readback) | item.hidden = true |
| Hide > All Artwork Above | `Selection Hat 4` | ✅ (readback) | item.hidden = true for items above |
| Hide > Other Layers | `Selection Hat 6` | ✅ (readback) | layer.visible = false for the other layers |
| Show All | `showAll` | ✅ (readback) | item.hidden = false (for all) |
| Expand | `Expand3` | ✅ (readback) | Object > Expand (dialog accepted): fill and stroke become separate paths |
| Expand Appearance | `expandStyle` | ✅ (readback) | AI.expandAppearance(item) |
| Crop Image | `Crop Image` | ✅ (readback) | Object > Crop Image (or executeMenuCommand('Crop Image')), drag a crop handle (tools/menu_ui.edge_drag), Enter commits |
| Rasterize | `Rasterize 8 menu item` | ✅ (readback) | document.rasterize(item, bounds, RasterizeOptions) / AI.rasterize() |
| Create Gradient Mesh | `make mesh` | ✅ (readback) | Object > Create Gradient Mesh (dialog accepted) |
| Create Object Mosaic | `AI Object Mosaic Plug-in4` | ✅ (readback) | Object > Create Object Mosaic (dialog accepted) |
| Create Trim Marks | `TrimMark v25` | ✅ (readback) | Object > Create Trim Marks |
| Flatten Transparency | `Flatten Transparency` | ✅ (readback) | Object > Flatten Transparency (dialog accepted) |
| Make Pixel Perfect | `Make Pixel Perfect` | ✅ (readback) | item.pixelAligned = true / MENU('Make Pixel Perfect') |
| Slice > Make | `AISlice Make Slice` | ✅ (readback) | item.sliced = true / MENU('AISlice Make Slice') |
| Slice > Release | `AISlice Release Slice` | ✅ (readback) | app.executeMenuCommand('AISlice Release Slice') |
| Slice > Create from Guides | `AISlice Create from Guides` | ✅ (deep) | app.executeMenuCommand('AISlice Create from Guides') |
| Slice > Create from Selection | `AISlice Create from Selection` | ✅ (deep) | app.executeMenuCommand('AISlice Create from Selection') |
| Slice > Duplicate Slice | `AISlice Duplicate` | ✅ (deep) | app.executeMenuCommand('AISlice Duplicate') |
| Slice > Combine Slices | `AISlice Combine` | ✅ (deep) | app.executeMenuCommand('AISlice Combine') |
| Slice > Divide Slices | `AISlice Divide` | ✅ (deep) | app.executeMenuCommand('AISlice Divide') |
| Slice > Delete All | `AISlice Delete All Slices` | ✅ (readback) | app.executeMenuCommand('AISlice Delete All Slices') |
| Slice > Slice Options | `AISlice Slice Options` | ✅ (deep) | app.executeMenuCommand('AISlice Slice Options') |
| Slice > Clip to Artboard | `AISlice Clip to Artboard` | ✅ (deep) | app.executeMenuCommand('AISlice Clip to Artboard') |
| Path > Join | `join` | ✅ (readback) | Object > Path > Join (two open paths) |
| Path > Average | `average` | ✅ (readback) | Object > Path > Average (dialog: both axes) |
| Path > Outline Stroke | `OffsetPath v22` | ✅ (readback) | Object > Path > Outline Stroke |
| Path > Offset Path | `OffsetPath v23` | ✅ (readback) | AI.offsetPath(item, d) + AI.expandAppearance(); menu: Offset Path dialog (offset typed) |
| Path > Reverse Path Direction | `Reverse Path Direction` | ✅ (readback) | app.executeMenuCommand('Reverse Path Direction') |
| Path > Simplify | `simplify menu item` | ✅ (readback) | Object > Path > Simplify via the menu bar; the on-canvas widget's automatic result is committed with Enter (121 -> ~10 points) |
| Path > Smooth | `smooth menu item` | ✅ (readback) | Object > Path > Smooth via the menu bar; the on-canvas slider is dragged (tools/menu_ui.widget_drag) and applies on release |
| Path > Add Anchor Points | `Add Anchor Points2` | ✅ (readback) | Object > Path > Add Anchor Points |
| Path > Remove Anchor Points | `Remove Anchor Points menu` | ✅ (readback) | Object > Path > Remove Anchor Points (selected anchors) |
| Path > Divide Objects Below | `Knife Tool2` | ✅ (fingerprint) | Object > Path > Divide Objects Below (top object cuts the ones below) |
| Path > Split Into Grid | `Rows and Columns....` | ✅ (readback) | Object > Path > Split Into Grid (dialog: rows 2, columns 2 set through UI Automation) |
| Path > Clean Up | `cleanup menu item` | ✅ (readback) | Object > Path > Clean Up (dialog: stray points, unpainted, empty text) |
| Shape > Convert to Shapes | `Convert to Shape` | ✅ (deep) | Object > Shape > Convert to Shapes (live shape) |
| Shape > Expand Shape | `Expand Shape` | ✅ (deep) | Object > Shape > Expand Shape |
| Pattern > Make | `Adobe Make Pattern` | ✅ (readback) | Object > Pattern > Make (enters pattern mode, adds a swatch); exit with MENU('exitFocus') |
| Pattern > Edit Pattern | `Adobe Edit Pattern` | ✅ (deep) | Object > Pattern > Edit Pattern on a pattern-filled object (enters pattern editing mode) |
| Pattern > Tile Edge Color | `Adobe Pattern Tile Color` | n/a | pattern-editing display option |
| Pattern > Text to Pattern (Beta) | `Text To Pattern` | n/a | generative AI / cloud feature (excluded by policy, like the Photoshop skill) |
| Repeat > Radial | `Make Radial Repeat` | ✅ (readback) | AI.repeat(item, 'radial') |
| Repeat > Grid | `Make Grid Repeat` | ✅ (readback) | AI.repeat(item, 'grid') |
| Repeat > Mirror | `Make Symmetry Repeat` | ✅ (readback) | AI.repeat(item, 'mirror') (nothing stays selected; readback document.symmetryRepeatItems) |
| Repeat > Release | `Release Repeat Art` | ✅ (readback) | app.executeMenuCommand('Release Repeat Art') |
| Repeat > Options | `Repeat Art Options` | ✅ (deep) | app.executeMenuCommand('Repeat Art Options') |
| Intertwine > Make | `Partial Rearrange Make` | ✅ (deep) | app.executeMenuCommand('Partial Rearrange Make') |
| Intertwine > Release | `Partial Rearrange Release` | ✅ (deep) | app.executeMenuCommand('Partial Rearrange Release') |
| Intertwine > Edit | `Partial Rearrange Edit` | ✅ (deep) | app.executeMenuCommand('Partial Rearrange Edit') |
| Blend > Make | `Path Blend Make` | ✅ (readback) | AI.blend([a, b]) |
| Blend > Release | `Path Blend Release` | ✅ (readback) | app.executeMenuCommand('Path Blend Release') |
| Blend > Blend Options | `Path Blend Options` | ✅ (deep) | Object > Blend > Blend Options (dialog: orientation 'Align to Path' clicked through UI Automation) |
| Blend > Expand | `Path Blend Expand` | ✅ (readback) | app.executeMenuCommand('Path Blend Expand') |
| Blend > Replace Spine | `Path Blend Replace Spine` | ✅ (deep) | app.executeMenuCommand('Path Blend Replace Spine') |
| Blend > Reverse Spine | `Path Blend Reverse Spine` | ✅ (deep) | app.executeMenuCommand('Path Blend Reverse Spine') |
| Blend > Reverse Front to Back | `Path Blend Reverse Stack` | ✅ (deep) | app.executeMenuCommand('Path Blend Reverse Stack') |
| Envelope Distort > Make with Warp | `Make Warp` | ✅ (readback) | Object > Envelope Distort > Make with Warp (dialog accepted) — or AI.warp() as a live effect |
| Envelope Distort > Make with Mesh | `Create Envelope Grid` | ✅ (readback) | Object > Envelope Distort > Make with Mesh (dialog accepted) |
| Envelope Distort > Make with Top Object | `Make Envelope` | ✅ (readback) | Object > Envelope Distort > Make with Top Object |
| Envelope Distort > Release | `Release Envelope` | ✅ (readback) | app.executeMenuCommand('Release Envelope') |
| Envelope Distort > Envelope Options | `Envelope Options` | ✅ (deep) | Object > Envelope Distort > Envelope Options (fidelity 90 through UI Automation) |
| Envelope Distort > Expand | `Expand Envelope` | ✅ (readback) | app.executeMenuCommand('Expand Envelope') |
| Envelope Distort > Edit Contents | `Edit Envelope Contents` | ✅ (deep) | Object > Envelope Distort > Edit Contents (the saved art records the envelope in contents-editing state) — via the menu bar: 物件 > 封套扭曲 > 編輯內容 (tools/menu_ui.py; app.executeMenuCommand refuses this id) |
| Perspective > Attach to Active Plane | `Attach to Active Plane` | ✅ (deep) | app.executeMenuCommand('Attach to Active Plane') |
| Perspective > Release with Perspective | `Release with Perspective` | ✅ (deep) | app.executeMenuCommand('Release with Perspective') |
| Perspective > Move Plane to Match Object | `Show Object Grid Plane` | ✅ (deep) | app.executeMenuCommand('Show Object Grid Plane') |
| Perspective > Edit Text | `Edit Original Object` | ✅ (deep) | app.executeMenuCommand('Edit Original Object') |
| Live Paint > Make | `Make Planet X` | ✅ (readback) | Object > Live Paint > Make |
| Live Paint > Merge | `Marge Planet X` | ✅ (deep) | app.executeMenuCommand('Marge Planet X') |
| Live Paint > Release | `Release Planet X` | ✅ (readback) | app.executeMenuCommand('Release Planet X') |
| Live Paint > Gap Options | `Planet X Options` | ✅ (deep) | app.executeMenuCommand('Planet X Options') |
| Live Paint > Expand | `Expand Planet X` | ✅ (readback) | app.executeMenuCommand('Expand Planet X') |
| Mockup (Beta) > Make | `Make Vector Edge` | n/a | generative AI / cloud feature (excluded by policy, like the Photoshop skill) |
| Mockup (Beta) > Release | `Release Vector Edge` | n/a | generative AI / cloud feature (excluded by policy, like the Photoshop skill) |
| Mockup (Beta) > Edit | `Edit Vector Edge` | n/a | generative AI / cloud feature (excluded by policy, like the Photoshop skill) |
| Image Trace > Make | `Make Image Tracing` | ✅ (readback) | rasterOrPlaced.trace() / AI.trace() |
| Image Trace > Make and Expand | `Make and Expand Image Tracing` | ✅ (readback) | AI.trace(item, preset, true) |
| Image Trace > Release | `Release Image Tracing` | ✅ (readback) | tracing.releaseTracing() |
| Image Trace > Expand | `Expand Image Tracing` | ✅ (readback) | tracing.expandTracing() |
| Text Wrap > Make | `Make Text Wrap` | ✅ (readback) | item.wrapped = true |
| Text Wrap > Release | `Release Text Wrap` | ✅ (readback) | item.wrapped = false |
| Text Wrap > Text Wrap Options | `Text Wrap Options...` | ✅ (readback) | item.wrapOffset / wrapInside |
| Clipping Mask > Make | `makeMask` | ✅ (readback) | AI.clip(mask, items) |
| Clipping Mask > Release | `releaseMask` | ✅ (readback) | app.executeMenuCommand('releaseMask') |
| Clipping Mask > Edit Mask | `editMask` | ✅ (readback) | Object > Clipping Mask > Edit Mask (the mask path gets selected) |
| Compound Path > Make | `compoundPath` | ✅ (readback) | AI.compound(paths) |
| Compound Path > Release | `noCompoundPath` | ✅ (readback) | app.executeMenuCommand('noCompoundPath') |
| Artboards > Convert to Artboards | `setCropMarks` | ✅ (readback) | document.artboards.add(rect) / AI.addArtboard() |
| Artboards > Rearrange All Artboards | `ReArrange Artboards` | ✅ (deep) | document.rearrangeArtboards(layout, rowsOrCols, spacing, moveArtwork) |
| Artboards > Fit to Artwork Bounds | `Fit Artboard to artwork bounds` | ✅ (readback) | AI.fitArtboard(i) |
| Artboards > Fit to Selected Art | `Fit Artboard to selected Art` | ✅ (readback) | document.fitArtboardToSelectedArt(i) / AI.fitArtboard(i, items) |
| Graph > Type | `setGraphStyle` | ✅ (deep) | Object > Graph > Type (dialog: chart type) |
| Graph > Data | `editGraphData` | ✅ (readback) | Object > Graph > Data (opens the data window) |
| Graph > Design | `graphDesigns` | ✅ (deep) | Object > Graph > Design: select the artwork, then New Design in the dialog (dialog plan: uiaclick 新增設計, OK) |
| Graph > Column | `setBarDesign` | ✅ (deep) | Object > Graph > Column |
| Graph > Marker | `setIconDesign` | ✅ (deep) | Object > Graph > Marker |
| Collect For Export > As Single Asset | `collectForExportSingleAsset` | ✅ (readback) | document.assets.add(group of the items) [menu ID refuses scripts: PARM] |
| Collect For Export > As Multiple Assets | `collectForExportMultipleAsset` | ✅ (readback) | document.assets.add(item) per item [menu ID refuses scripts: PARM] |

## Type

| Command | executeMenuCommand | Status | How (script) |
|---|---|---|---|
| More from Adobe Fonts | `Browse Typekit Fonts Menu IllustratorUI` | n/a | font service / panel / display only |
| Glyphs | `alternate glyph palette plugin` | n/a | font service / panel / display only |
| Convert To Area Type / Point Type | `point-area` | ✅ (readback) | textFrame.convertPointObjectToAreaObject() [menu ID refuses scripts: PARM] |
| Area Type Options | `areatextoptions` | ✅ (readback) | textFrame.columnCount / rowCount / columnGutter / rowGutter / spacing / firstBaseline |
| Type on a Path > Rainbow | `textpathtypeRainbow` | ✅ (pixels) | Type > Type on a Path > Rainbow (from Skew; Rainbow is the default) — via the menu bar: 文字 > 路徑文字 > 彩虹效果 (tools/menu_ui.py; app.executeMenuCommand refuses this id) |
| Type on a Path > Skew | `textpathtypeSkew` | ✅ (pixels) | Type > Type on a Path > Skew — via the menu bar: 文字 > 路徑文字 > 偏斜效果 (tools/menu_ui.py; app.executeMenuCommand refuses this id) |
| Type on a Path > 3D Ribbon | `textpathtype3d` | ✅ (pixels) | Type > Type on a Path > 3d — via the menu bar: 文字 > 路徑文字 > 3D 帶狀效果 (tools/menu_ui.py; app.executeMenuCommand refuses this id) |
| Type on a Path > Stair Step | `textpathtypestairs` | ✅ (pixels) | Type > Type on a Path > stairs — via the menu bar: 文字 > 路徑文字 > 階梯效果 (tools/menu_ui.py; app.executeMenuCommand refuses this id) |
| Type on a Path > Gravity | `textpathtypeGravity` | ✅ (pixels) | Type > Type on a Path > Gravity — via the menu bar: 文字 > 路徑文字 > 重力效果 (tools/menu_ui.py; app.executeMenuCommand refuses this id) |
| Type on a Path > Type on a Path Options | `textpathtypeOptions` | ✅ (pixels) | Type > Type on a Path > Options (dialog: Flip toggled) — via the menu bar: 文字 > 路徑文字 > 路徑文字選項 (tools/menu_ui.py; app.executeMenuCommand refuses this id) |
| Type on a Path > Update Legacy Type on a Path | `updateLegacyTOP` | ✅ (deep) | Type > Type on a Path > Update Legacy Type on a Path (legacy file) |
| Composite Fonts | `Adobe internal composite font plugin` | n/a | CJK set editors (settings dialogs); applying a set is paragraphAttributes.kinsoku / mojikumi |
| Kinsoku Shori Settings | `Adobe Kinsoku Settings` | n/a | CJK set editors (settings dialogs); applying a set is paragraphAttributes.kinsoku / mojikumi |
| Mojikumi Settings | `Adobe MojiKumi Settings` | n/a | CJK set editors (settings dialogs); applying a set is paragraphAttributes.kinsoku / mojikumi |
| Threaded Text > Create | `threadTextCreate` | ✅ (readback) | Type > Threaded Text > Create (area text + an empty path) |
| Threaded Text > Release Selection | `releaseThreadedTextSelection` | ✅ (readback) | Type > Threaded Text > Release Selection (the selected frame leaves the thread) — via the menu bar: 文字 > 文字緒 > 釋放選取的文字物件 (tools/menu_ui.py; app.executeMenuCommand refuses this id) |
| Threaded Text > Remove Threading | `removeThreading` | ✅ (readback) | Type > Threaded Text > Remove Threading (every frame keeps its text, the thread is gone) — via the menu bar: 文字 > 文字緒 > 移除文字緒 (tools/menu_ui.py; app.executeMenuCommand refuses this id) |
| Fit Headline | `fitHeadline` | ✅ (readback) | AI.fitHeadline(frame): largest tracking that keeps the line on one line of the frame (the menu needs a text cursor) |
| Resolve Missing Fonts | `Adobe IllustratorUI Resolve Missing Font` | n/a | font service / panel / display only |
| Find/Replace Font | `Adobe Illustrator Find Font Menu Item` | ✅ (readback) | characterAttributes.textFont = app.textFonts.getByName(...) (Find/Replace Font) |
| Change Case > UPPERCASE | `UpperCase Change Case Item` | ✅ (readback) | app.executeMenuCommand('UpperCase Change Case Item') |
| Change Case > lowercase | `LowerCase Change Case Item` | ✅ (readback) | app.executeMenuCommand('LowerCase Change Case Item') |
| Change Case > Title Case | `Title Case Change Case Item` | ✅ (readback) | app.executeMenuCommand('Title Case Change Case Item') |
| Change Case > Sentence case | `Sentence case Change Case Item` | ✅ (readback) | app.executeMenuCommand('Sentence case Change Case Item') |
| Smart Punctuation | `Adobe Illustrator Smart Punctuation Menu Item` | ✅ (readback) | Type > Smart Punctuation (dialog accepted) |
| Create Outlines | `outline` | ✅ (readback) | textFrame.createOutline() / AI.outline() |
| Optical Margin Alignment | `Adobe Optical Alignment Item` | ✅ (readback) | textFrame.opticalAlignment = true |
| Insert Special Character > Symbols > Bullet | `~bullet` | ✅ (readback) | characters[i].contents = '\u2022' [menu ID refuses scripts: PARM] |
| Insert Special Character > Symbols > Copyright Symbol | `~copyright` | ✅ (readback) | characters[i].contents = '\u00A9' [menu ID refuses scripts: PARM] |
| Insert Special Character > Symbols > Ellipsis | `~ellipsis` | ✅ (readback) | characters[i].contents = '\u2026' [menu ID refuses scripts: PARM] |
| Insert Special Character > Symbols > Paragraph Symbol | `~paragraphSymbol` | ✅ (readback) | characters[i].contents = '\u00B6' [menu ID refuses scripts: PARM] |
| Insert Special Character > Symbols > Registered Trademark Symbol | `~registeredTrademark` | ✅ (readback) | characters[i].contents = '\u00AE' [menu ID refuses scripts: PARM] |
| Insert Special Character > Symbols > Section Symbol | `~sectionSymbol` | ✅ (readback) | characters[i].contents = '\u00A7' [menu ID refuses scripts: PARM] |
| Insert Special Character > Symbols > Trademark Symbol | `~trademarkSymbol` | ✅ (readback) | characters[i].contents = '\u2122' [menu ID refuses scripts: PARM] |
| Insert Special Character > Hyphens and Dashes > Em Dash | `~emDash` | ✅ (readback) | characters[i].contents = '\u2014' [menu ID refuses scripts: PARM] |
| Insert Special Character > Hyphens and Dashes > En Dash | `~enDash` | ✅ (readback) | characters[i].contents = '\u2013' [menu ID refuses scripts: PARM] |
| Insert Special Character > Hyphens and Dashes > Discretionary Hyphen | `~discretionaryHyphen` | ✅ (readback) | characters[i].contents = '\u00AD' [menu ID refuses scripts: PARM] |
| Insert Special Character > Quotation Marks > Double Left Quotation Marks | `~doubleLeftQuote` | ✅ (readback) | characters[i].contents = '\u201C' [menu ID refuses scripts: PARM] |
| Insert Special Character > Quotation Marks > Double Right Quotation Marks | `~doubleRightQuote` | ✅ (readback) | characters[i].contents = '\u201D' [menu ID refuses scripts: PARM] |
| Insert Special Character > Quotation Marks > Single Left Quotation Mark | `~singleLeftQuote` | ✅ (readback) | characters[i].contents = '\u2018' [menu ID refuses scripts: PARM] |
| Insert Special Character > Quotation Marks > Single Right Quotation Mark | `~singleRightQuote` | ✅ (readback) | characters[i].contents = '\u2019' [menu ID refuses scripts: PARM] |
| Insert Whitespace Character > Em Space | `~emSpace` | ✅ (readback) | characters[i].contents = '\u2003' [menu ID refuses scripts: PARM] |
| Insert Whitespace Character > En Space | `~enSpace` | ✅ (readback) | characters[i].contents = '\u2002' [menu ID refuses scripts: PARM] |
| Insert Whitespace Character > Hair Space | `~hairSpace` | ✅ (readback) | characters[i].contents = '\u200A' [menu ID refuses scripts: PARM] |
| Insert Whitespace Character > Thin Space | `~thinSpace` | ✅ (readback) | characters[i].contents = '\u2009' [menu ID refuses scripts: PARM] |
| Insert Break Character > Forced Line Break | `~forcedLineBreak` | ✅ (readback) | characters[i].contents = '\u0003' [menu ID refuses scripts: PARM] |
| Fill with Placeholder Text | `~placeHolderText` | ✅ (readback) | textFrame.contents = placeholder text [menu ID refuses scripts: PARM] |
| Show Hidden Characters | `showHiddenChar` | n/a | font service / panel / display only |
| Type Orientation > Horizontal | `type-horizontal` | ✅ (readback) | textFrame.orientation = TextOrientation.HORIZONTAL |
| Type Orientation > Vertical | `type-vertical` | ✅ (readback) | textFrame.orientation = TextOrientation.VERTICAL |
| Legacy Text > Update All Legacy Text | `convertlegacyText` | ✅ (readback) | legacyTextItems[i].convertToNative() for all [menu ID refuses scripts: PARM] |
| Legacy Text > Update Selected Legacy Text | `convertlegacyText1` | ✅ (readback) | legacyTextItem.convertToNative() [menu ID refuses scripts: PARM] |
| Legacy Text > Hide Copies | `convertlegacyText2` | ✅ (readback) | legacyTextItem.hidden = true (hide copies) [menu ID refuses scripts: PARM] |
| Legacy Text > Delete Copies | `convertlegacyText3` | ✅ (readback) | legacyTextItem.remove() (delete copies) [menu ID refuses scripts: PARM] |
| Legacy Text > Select Copies | `convertlegacyText4` | ✅ (readback) | legacyTextItem.selected = true (select copies) [menu ID refuses scripts: PARM] |

## Select

| Command | executeMenuCommand | Status | How (script) |
|---|---|---|---|
| All | `selectall` | ✅ (readback) | item.selected = true for every item / document.selection = items |
| All on Active Artboard | `selectallinartboard` | ✅ (readback) | document.selectObjectsOnActiveArtboard() |
| Deselect | `deselectall` | ✅ (readback) | document.selection = null |
| Reselect | `Find Reselect menu item` | ✅ (readback) | app.executeMenuCommand('Find Reselect menu item') |
| Inverse | `Inverse menu item` | ✅ (readback) | select every item that is not selected |
| Next Object Above | `Selection Hat 8` | ✅ (readback) | select the item with the next higher absoluteZOrderPosition |
| Next Object Below | `Selection Hat 9` | ✅ (readback) | select the item with the next lower absoluteZOrderPosition |
| Same > Appearance | `Find Appearance menu item` | ✅ (readback) | compare appearance (fill, stroke, effects) and select matches |
| Same > Appearance Attribute | `Find Appearance Attributes menu item` | ✅ (readback) | select items sharing a live effect |
| Same > Blending Mode | `Find Blending Mode menu item` | ✅ (readback) | select items with the same blendingMode |
| Same > Fill & Stroke | `Find Fill & Stroke menu item` | ✅ (readback) | select items with equal fillColor and strokeColor |
| Same > Fill Color | `Find Fill Color menu item` | ✅ (readback) | select items with equal fillColor |
| Same > Opacity | `Find Opacity menu item` | ✅ (readback) | select items with equal opacity |
| Same > Stroke Color | `Find Stroke Color menu item` | ✅ (readback) | select items with equal strokeColor |
| Same > Stroke Weight | `Find Stroke Weight menu item` | ✅ (readback) | select items with equal strokeWidth |
| Same > Graphic Style | `Find Style menu item` | ✅ (readback) | select items with the same graphic style |
| Same > Shape | `Find Live Shape menu item` | ✅ (readback) | select live shapes of the same kind |
| Same > Symbol Instance | `Find Symbol Instance menu item` | ✅ (readback) | select symbolItems whose .symbol is the same |
| Same > Link Block Series | `Find Link Block Series menu item` | ✅ (readback) | select the frames of one story (textFrame.story.textFrames) |
| Same > Font Family | `Find Text Font Family menu item` | ✅ (readback) | compare characterAttributes (textFont, size, fillColor, strokeColor) across textFrames |
| Same > Font Family & Style | `Find Text Font Family Style menu item` | ✅ (readback) | compare characterAttributes (textFont, size, fillColor, strokeColor) across textFrames |
| Same > Font Family, Style & Size | `Find Text Font Family Style Size menu item` | ✅ (readback) | compare characterAttributes (textFont, size, fillColor, strokeColor) across textFrames |
| Same > Font Size | `Find Text Font Size menu item` | ✅ (readback) | compare characterAttributes (textFont, size, fillColor, strokeColor) across textFrames |
| Same > Text Fill Color | `Find Text Fill Color menu item` | ✅ (readback) | compare characterAttributes (textFont, size, fillColor, strokeColor) across textFrames |
| Same > Text Stroke Color | `Find Text Stroke Color menu item` | ✅ (readback) | compare characterAttributes (textFont, size, fillColor, strokeColor) across textFrames |
| Same > Text Fill & Stroke Color | `Find Text Fill Stroke Color menu item` | ✅ (readback) | compare characterAttributes (textFont, size, fillColor, strokeColor) across textFrames |
| Object > All on Same Layers | `Selection Hat 3` | ✅ (readback) | select every item of item.layer |
| Object > Direction Handles | `Selection Hat 1` | ✅ (readback) | pathPoint.selected = PathPointSelection.* |
| Object > Bristle Brush Strokes | `Bristle Brush Strokes menu item` | ✅ (readback) | Select > Object > Bristle Brush Strokes (in a document that has bristle brushes: the shipped Bristle Brush library) |
| Object > Brush Strokes | `Brush Strokes menu item` | ✅ (readback) | brush.applyTo(path); select paths that have a brush |
| Object > Clipping Masks | `Clipping Masks menu item` | ✅ (readback) | select pathItems with clipping == true |
| Object > Stray Points | `Stray Points menu item` | ✅ (readback) | select pathItems with a single point |
| Object > All Text Objects | `Text Objects menu item` | ✅ (readback) | select every textFrame |
| Object > Point Text Objects | `Point Text Objects menu item` | ✅ (readback) | select textFrames with kind POINTTEXT |
| Object > Area Text Objects | `Area Text Objects menu item` | ✅ (readback) | select textFrames with kind AREATEXT |
| Start Global Edit | `SmartEdit Menu Item` | ✅ (readback) | Select > Start Global Edit |
| Save Selection | `Selection Hat 10` | ✅ (deep) | Select > Save Selection (name typed) |
| Edit Selection | `Selection Hat 11` | ✅ (deep) | Select > Edit Selection (dialog: the saved selection 'MySel' deleted through UI Automation) |
| Update Selection | `Selection Hat 14` | ✅ (readback) | Select > Update Selection (choose saved 'MySel', add an object, update; re-choosing 'MySel' now selects 2 objects) — via the menu bar: 選取 > 更新選取範圍 (tools/menu_ui.py; app.executeMenuCommand refuses this id) |

## Effect

| Command | executeMenuCommand | Status | How (script) |
|---|---|---|---|
| Apply Last Effect | `Adobe Apply Last Effect` | ✅ (deep) | app.executeMenuCommand('Adobe Apply Last Effect') |
| Last Effect | `Adobe Last Effect` | ✅ (deep) | app.executeMenuCommand('Adobe Last Effect') |
| Document Raster Effects Settings | `Live Rasterize Effect Setting` | ✅ (readback) | document.rasterEffectSettings.resolution / .transparency / .padding ... |
| 3D and Materials > Extrude & Bevel | `Live Adobe Geometry3D Extrude` | ✅ (effect readback) | AI.fx(item, 'Adobe Geometry3D', {…}) = applyEffect(XML); menu command verified too (Adobe Geometry3D: 36 params read back, Geometry3DkSunlightRotationKey changed to 218.5) |
| 3D and Materials > Revolve | `Live Adobe Geometry3D Revolve` | ✅ (effect readback) | AI.fx(item, 'Adobe Geometry3D', {…}) = applyEffect(XML); menu command verified too (Adobe Geometry3D: 38 params read back, Geometry3DkSunlightRotationKey changed to 218.5) |
| 3D and Materials > Inflate | `Live Adobe Geometry3D Inflate` | ✅ (effect readback) | AI.fx(item, 'Adobe Geometry3D', {…}) = applyEffect(XML); menu command verified too (Adobe Geometry3D: 38 params read back, Geometry3DkSunlightRotationKey changed to 218.5) |
| 3D and Materials > Rotate | `Live Adobe Geometry3D Rotate` | ✅ (effect readback) | AI.fx(item, 'Adobe Geometry3D', {…}) = applyEffect(XML); menu command verified too (Adobe Geometry3D: 36 params read back, Geometry3DkSunlightRotationKey changed to 218.5) |
| 3D and Materials > Materials | `Live Adobe Geometry3D Materials` | ✅ (effect readback) | AI.fx(item, 'Adobe Geometry3D', {…}) = applyEffect(XML); menu command verified too (Adobe Geometry3D: 36 params read back, Geometry3DkSunlightRotationKey changed to 218.5) |
| 3D and Materials > 3D (Classic) > Extrude & Bevel (Classic) | `Live 3DExtrude` | ✅ (effect readback) | AI.fx(item, 'Adobe 3D Effect', {…}) = applyEffect(XML); menu command verified too (Adobe 3D Effect: 51 params read back, revolveAngle changed to 541.0) |
| 3D and Materials > 3D (Classic) > Revolve (Classic) | `Live 3DRevolve` | ✅ (effect readback) | AI.fx(item, 'Adobe 3D Effect', {…}) = applyEffect(XML); menu command verified too (Adobe 3D Effect: 51 params read back, revolveAngle changed to 541.0) |
| 3D and Materials > 3D (Classic) > Rotate (Classic) | `Live 3DRotate` | ✅ (effect readback) | AI.fx(item, 'Adobe 3D Effect', {…}) = applyEffect(XML); menu command verified too (Adobe 3D Effect: 51 params read back, revolveAngle changed to 541.0) |
| SVG Filters > Apply SVG Filter | `Live SVG Filters` | ✅ (effect readback) | AI.fx(item, 'Adobe SVG Filter Effect', {…}) = applyEffect(XML); menu command verified too (Adobe SVG Filter Effect: 0 params read back) |
| SVG Filters > Import SVG Filter | `SVG Filter Import` | ✅ (deep) | Effect > SVG Filters > Import SVG Filter (file typed into the open dialog) |
| Warp > Arc | `Live Deform Arc` | ✅ (effect readback) | AI.fx(item, 'Adobe Deform', {…}) = applyEffect(XML); menu command verified too (Adobe Deform: 5 params read back, DeformHoriz changed to 1.0) |
| Warp > Arc Lower | `Live Deform Arc Lower` | ✅ (effect readback) | AI.fx(item, 'Adobe Deform', {…}) = applyEffect(XML); menu command verified too (Adobe Deform: 5 params read back, DeformHoriz changed to 1.0) |
| Warp > Arc Upper | `Live Deform Arc Upper` | ✅ (effect readback) | AI.fx(item, 'Adobe Deform', {…}) = applyEffect(XML); menu command verified too (Adobe Deform: 5 params read back, DeformHoriz changed to 1.0) |
| Warp > Arch | `Live Deform Arch` | ✅ (effect readback) | AI.fx(item, 'Adobe Deform', {…}) = applyEffect(XML); menu command verified too (Adobe Deform: 5 params read back, DeformHoriz changed to 1.0) |
| Warp > Bulge | `Live Deform Bulge` | ✅ (effect readback) | AI.fx(item, 'Adobe Deform', {…}) = applyEffect(XML); menu command verified too (Adobe Deform: 5 params read back, DeformHoriz changed to 1.0) |
| Warp > Shell Lower | `Live Deform Shell Lower` | ✅ (effect readback) | AI.fx(item, 'Adobe Deform', {…}) = applyEffect(XML); menu command verified too (Adobe Deform: 5 params read back, DeformHoriz changed to 1.0) |
| Warp > Shell Upper | `Live Deform Shell Upper` | ✅ (effect readback) | AI.fx(item, 'Adobe Deform', {…}) = applyEffect(XML); menu command verified too (Adobe Deform: 5 params read back, DeformHoriz changed to 1.0) |
| Warp > Flag | `Live Deform Flag` | ✅ (effect readback) | AI.fx(item, 'Adobe Deform', {…}) = applyEffect(XML); menu command verified too (Adobe Deform: 5 params read back, DeformHoriz changed to 1.0) |
| Warp > Wave | `Live Deform Wave` | ✅ (effect readback) | AI.fx(item, 'Adobe Deform', {…}) = applyEffect(XML); menu command verified too (Adobe Deform: 5 params read back, DeformHoriz changed to 1.0) |
| Warp > Fish | `Live Deform Fish` | ✅ (effect readback) | AI.fx(item, 'Adobe Deform', {…}) = applyEffect(XML); menu command verified too (Adobe Deform: 5 params read back, DeformHoriz changed to 1.0) |
| Warp > Rise | `Live Deform Rise` | ✅ (effect readback) | AI.fx(item, 'Adobe Deform', {…}) = applyEffect(XML); menu command verified too (Adobe Deform: 5 params read back, DeformHoriz changed to 1.0) |
| Warp > Fisheye | `Live Deform Fisheye` | ✅ (effect readback) | AI.fx(item, 'Adobe Deform', {…}) = applyEffect(XML); menu command verified too (Adobe Deform: 5 params read back, DeformHoriz changed to 1.0) |
| Warp > Inflate | `Live Deform Inflate` | ✅ (effect readback) | AI.fx(item, 'Adobe Deform', {…}) = applyEffect(XML); menu command verified too (Adobe Deform: 5 params read back, DeformHoriz changed to 1.0) |
| Warp > Squeeze | `Live Deform Squeeze` | ✅ (effect readback) | AI.fx(item, 'Adobe Deform', {…}) = applyEffect(XML); menu command verified too (Adobe Deform: 5 params read back, DeformHoriz changed to 1.0) |
| Warp > Twist | `Live Deform Twist` | ✅ (effect readback) | AI.fx(item, 'Adobe Deform', {…}) = applyEffect(XML); menu command verified too (Adobe Deform: 5 params read back, DeformHoriz changed to 1.0) |
| Distort & Transform > Roughen | `Live Roughen` | ✅ (effect readback) | AI.fx(item, 'Adobe Roughen', {…}) = applyEffect(XML); menu command verified too (Adobe Roughen: 5 params read back, dtal changed to 16.0) |
| Distort & Transform > Pucker & Bloat | `Live Pucker & Bloat` | ✅ (effect readback) | AI.fx(item, 'Adobe Punk and Bloat', {…}) = applyEffect(XML); menu command verified too (Adobe Punk and Bloat: 1 params read back, d_factor changed to 1.0) |
| Distort & Transform > Twist | `Live Twist` | ✅ (effect readback) | AI.fx(item, 'Adobe Twirl', {…}) = applyEffect(XML); menu command verified too (Adobe Twirl: 1 params read back, angle changed to 1.0) |
| Distort & Transform > Transform | `Live Transform` | ✅ (effect readback) | AI.fx(item, 'Adobe Transform', {…}) = applyEffect(XML); menu command verified too (Adobe Transform: 16 params read back, scaleH_Factor changed to 2.5) |
| Distort & Transform > Zig Zag | `Live Zig Zag` | ✅ (effect readback) | AI.fx(item, 'Adobe Zigzag', {…}) = applyEffect(XML); menu command verified too (Adobe Zigzag: 5 params read back, amount changed to 16.0) |
| Distort & Transform > Free Distort | `Live Free Distort` | ✅ (effect readback) | AI.fx(item, 'Adobe Free Distort', {…}) = applyEffect(XML); menu command verified too (Adobe Free Distort: 16 params read back, src3h changed to 751.0) |
| Distort & Transform > Tweak | `Live Scribble and Tweak` | ✅ (effect readback) | AI.fx(item, 'Adobe Scribble and Tweak', {…}) = applyEffect(XML); menu command verified too (Adobe Scribble and Tweak: 8 params read back, vert changed to 16.0) |
| Crop Marks | `Live Trim Marks` | ✅ (effect readback) | AI.fx(item, 'Adobe Trim Marks', {…}) = applyEffect(XML); menu command verified too (Adobe Trim Marks: 1 params read back, styl changed to 1) |
| Path > Offset Path | `Live Offset Path` | ✅ (effect readback) | AI.fx(item, 'Adobe Offset Path', {…}) = applyEffect(XML); menu command verified too (Adobe Offset Path: 3 params read back, ofst changed to 16.0) |
| Path > Outline Object | `Live Outline Object` | ✅ (effect readback) | AI.fx(item, 'Adobe Outline Type', {…}) = applyEffect(XML); menu command verified too (Adobe Outline Type: 0 params read back) |
| Path > Outline Stroke | `Live Outline Stroke` | ✅ (effect readback) | AI.fx(item, 'Adobe Outline Stroke', {…}) = applyEffect(XML); menu command verified too (Adobe Outline Stroke: 0 params read back) |
| Pathfinder > Add | `Live Pathfinder Add` | ✅ (effect readback) | AI.fx(item, 'Adobe Pathfinder', {…}) = applyEffect(XML); menu command verified too (Adobe Pathfinder: 13 params read back, TrapAspect changed to 2.5) |
| Pathfinder > Intersect | `Live Pathfinder Intersect` | ✅ (effect readback) | AI.fx(item, 'Adobe Pathfinder', {…}) = applyEffect(XML); menu command verified too (Adobe Pathfinder: 13 params read back, TrapAspect changed to 2.5) |
| Pathfinder > Exclude | `Live Pathfinder Exclude` | ✅ (effect readback) | AI.fx(item, 'Adobe Pathfinder', {…}) = applyEffect(XML); menu command verified too (Adobe Pathfinder: 13 params read back, TrapAspect changed to 2.5) |
| Pathfinder > Subtract | `Live Pathfinder Subtract` | ✅ (effect readback) | AI.fx(item, 'Adobe Pathfinder', {…}) = applyEffect(XML); menu command verified too (Adobe Pathfinder: 13 params read back, Mix changed to 1.75) |
| Pathfinder > Minus Back | `Live Pathfinder Minus Back` | ✅ (effect readback) | AI.fx(item, 'Adobe Pathfinder', {…}) = applyEffect(XML); menu command verified too (Adobe Pathfinder: 13 params read back, TrapAspect changed to 2.5) |
| Pathfinder > Divide | `Live Pathfinder Divide` | ✅ (effect readback) | AI.fx(item, 'Adobe Pathfinder', {…}) = applyEffect(XML); menu command verified too (Adobe Pathfinder: 13 params read back, TrapAspect changed to 2.5) |
| Pathfinder > Trim | `Live Pathfinder Trim` | ✅ (effect readback) | AI.fx(item, 'Adobe Pathfinder', {…}) = applyEffect(XML); menu command verified too (Adobe Pathfinder: 13 params read back, TrapAspect changed to 2.5) |
| Pathfinder > Merge | `Live Pathfinder Merge` | ✅ (effect readback) | AI.fx(item, 'Adobe Pathfinder', {…}) = applyEffect(XML); menu command verified too (Adobe Pathfinder: 13 params read back, TrapAspect changed to 2.5) |
| Pathfinder > Crop | `Live Pathfinder Crop` | ✅ (effect readback) | AI.fx(item, 'Adobe Pathfinder', {…}) = applyEffect(XML); menu command verified too (Adobe Pathfinder: 13 params read back, Mix changed to 1.75) |
| Pathfinder > Outline | `Live Pathfinder Outline` | ✅ (effect readback) | AI.fx(item, 'Adobe Pathfinder', {…}) = applyEffect(XML); menu command verified too (Adobe Pathfinder: 13 params read back, Mix changed to 1.75) |
| Pathfinder > Hard Mix | `Live Pathfinder Hard Mix` | ✅ (effect readback) | AI.fx(item, 'Adobe Pathfinder', {…}) = applyEffect(XML); menu command verified too (Adobe Pathfinder: 13 params read back, Precision changed to 16.0) |
| Pathfinder > Soft Mix | `Live Pathfinder Soft Mix` | ✅ (effect readback) | AI.fx(item, 'Adobe Pathfinder', {…}) = applyEffect(XML); menu command verified too (Adobe Pathfinder: 13 params read back, Precision changed to 16.0) |
| Pathfinder > Trap | `Live Pathfinder Trap` | ✅ (effect readback) | AI.fx(item, 'Adobe Pathfinder', {…}) = applyEffect(XML); menu command verified too (Adobe Pathfinder: 13 params read back, Precision changed to 16.0) |
| Convert to Shape > Rectangle | `Live Rectangle` | ✅ (effect readback) | AI.fx(item, 'Adobe Shape Effects', {…}) = applyEffect(XML); menu command verified too (Adobe Shape Effects: 7 params read back, AbsHeight changed to 55.0) |
| Convert to Shape > Rounded Rectangle | `Live Rounded Rectangle` | ✅ (effect readback) | AI.fx(item, 'Adobe Shape Effects', {…}) = applyEffect(XML); menu command verified too (Adobe Shape Effects: 7 params read back, AbsHeight changed to 55.0) |
| Convert to Shape > Ellipse | `Live Ellipse` | ✅ (effect readback) | AI.fx(item, 'Adobe Shape Effects', {…}) = applyEffect(XML); menu command verified too (Adobe Shape Effects: 7 params read back, AbsHeight changed to 55.0) |
| Stylize > Inner Glow | `Live Inner Glow` | ✅ (effect readback) | AI.fx(item, 'Adobe Inner Glow', {…}) = applyEffect(XML); menu command verified too (Adobe Inner Glow: 4 params read back, blur changed to 8.5) |
| Stylize > Round Corners | `Live Adobe Round Corners` | ✅ (effect readback) | AI.fx(item, 'Adobe Round Corners', {…}) = applyEffect(XML); menu command verified too (Adobe Round Corners: 1 params read back, radius changed to 16.0) |
| Stylize > Scribble | `Live Scribble Fill` | ✅ (effect readback) | AI.fx(item, 'Adobe Scribble Fill', {…}) = applyEffect(XML); menu command verified too (Adobe Scribble Fill: 8 params read back, Angle changed to 46.0) |
| Stylize > Outer Glow | `Live Outer Glow` | ✅ (effect readback) | AI.fx(item, 'Adobe Outer Glow', {…}) = applyEffect(XML); menu command verified too (Adobe Outer Glow: 4 params read back, blur changed to 8.5) |
| Stylize > Feather | `Live Feather` | ✅ (effect readback) | AI.fx(item, 'Adobe Fuzzy Mask', {…}) = applyEffect(XML); menu command verified too (Adobe Fuzzy Mask: 1 params read back, Radius changed to 8.5) |
| Stylize > Drop Shadow | `Live Adobe Drop Shadow` | ✅ (effect readback) | AI.fx(item, 'Adobe Drop Shadow', {…}) = applyEffect(XML); menu command verified too (Adobe Drop Shadow: 9 params read back, dark changed to 151.0) |
| Rasterize | `Live Rasterize` | ✅ (effect readback) | AI.fx(item, 'Adobe Rasterize', {…}) = applyEffect(XML); menu command verified too (Adobe Rasterize: 6 params read back, padd changed to 55.0) |
| Effect Gallery | `Live PSAdapter_plugin_GEfc` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_Gls ', {…}) = applyEffect(XML); menu command verified too (UI: gallery filter chosen by click -> PSAdapter_plugin_Gls  {'GEfk': 'Gls ', 'Dstr': 5, 'Smth': 3, 'TxtT': 'TxFr', 'Scln': 100, 'InvT': False} read back; each gallery filter also has its own command) |
| Pixelate > Color Halftone | `Live PSAdapter_plugin_ClrH` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_ClrH', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_ClrH: XML applies it with defaults; dialog field 0 typed 9 -> descriptor Rds =9 read back) |
| Pixelate > Crystallize | `Live PSAdapter_plugin_Crst` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_Crst', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_Crst: XML applies it with defaults; dialog field 0 typed 11 -> descriptor ClSz=11 read back) |
| Pixelate > Mezzotint | `Live PSAdapter_plugin_Mztn` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_Mztn', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_Mztn: applyEffect adds it with its defaults ({'MztT': 'FnDt', 'FlRs': 15985656}); no numeric dialog field to set) |
| Pixelate > Pointillize | `Live PSAdapter_plugin_Pntl` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_Pntl', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_Pntl: XML applies it with defaults; dialog field 0 typed 6 -> descriptor ClSz=6 read back) |
| Distort > Diffuse Glow | `Live PSAdapter_plugin_DfsG` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_DfsG', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_DfsG: XML applies it with defaults; dialog field 0 typed 7 -> descriptor Grns=7 read back) |
| Distort > Ocean Ripple | `Live PSAdapter_plugin_OcnR` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_OcnR', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_OcnR: XML applies it with defaults; dialog field 0 typed 10 -> descriptor RplS=10 read back) |
| Distort > Glass | `Live PSAdapter_plugin_Gls ` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_Gls ', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_Gls : XML applies it with defaults; dialog field 0 typed 7 -> descriptor Dstr=7 read back) |
| Blur > Radial Blur | `Live PSAdapter_plugin_RdlB` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_RdlB', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_RdlB: XML applies it with defaults; dialog field 0 typed 11 -> descriptor Amnt=11 read back) |
| Blur > Smart Blur | `Live PSAdapter_plugin_SmrB` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_SmrB', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_SmrB: applyEffect adds it with its defaults ({'Rds ': 3.0, 'Thsh': 25.0, 'SmBQ': 'SBQL', 'SmBM': 'SBMN'}); no numeric dialog field to set) |
| Blur > Gaussian Blur | `Live Adobe PSL Gaussian Blur` | ✅ (effect readback) | AI.fx(item, 'Adobe PSL Gaussian Blur', {…}) = applyEffect(XML); menu command verified too (Adobe PSL Gaussian Blur: 3 params read back, blur changed to 16.0) |
| Brush Strokes > Crosshatch | `Live PSAdapter_plugin_Crsh` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_Crsh', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_Crsh: XML applies it with defaults; dialog field 0 typed 11 -> descriptor StrL=11 read back) |
| Brush Strokes > Sprayed Strokes | `Live PSAdapter_plugin_SprS` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_SprS', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_SprS: XML applies it with defaults; dialog field 0 typed 13 -> descriptor StrL=13 read back) |
| Brush Strokes > Sumi-e | `Live PSAdapter_plugin_Smie` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_Smie', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_Smie: XML applies it with defaults; dialog field 0 typed 11 -> descriptor StrW=11 read back) |
| Brush Strokes > Accented Edges | `Live PSAdapter_plugin_AccE` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_AccE', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_AccE: XML applies it with defaults; dialog field 0 typed 3 -> descriptor EdgW=3 read back) |
| Brush Strokes > Ink Outlines | `Live PSAdapter_plugin_InkO` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_InkO', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_InkO: XML applies it with defaults; dialog field 0 typed 5 -> descriptor StrL=5 read back) |
| Brush Strokes > Spatter | `Live PSAdapter_plugin_Spt ` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_Spt ', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_Spt : XML applies it with defaults; dialog field 0 typed 12 -> descriptor SprR=12 read back) |
| Brush Strokes > Angled Strokes | `Live PSAdapter_plugin_AngS` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_AngS', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_AngS: XML applies it with defaults; dialog field 0 typed 51 -> descriptor DrcB=51 read back) |
| Brush Strokes > Dark Strokes | `Live PSAdapter_plugin_DrkS` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_DrkS', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_DrkS: XML applies it with defaults; dialog field 0 typed 6 -> descriptor BlcI=6 read back) |
| Texture > Mosaic Tiles | `Live PSAdapter_plugin_MscT` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_MscT', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_MscT: XML applies it with defaults; dialog field 0 typed 99 -> descriptor TlSz=99 read back) |
| Texture > Stained Glass | `Live PSAdapter_plugin_StnG` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_StnG', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_StnG: XML applies it with defaults; dialog field 0 typed 11 -> descriptor ClSz=11 read back) |
| Texture > Patchwork | `Live PSAdapter_plugin_Ptch` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_Ptch', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_Ptch: XML applies it with defaults; dialog field 0 typed 5 -> descriptor SqrS=5 read back) |
| Texture > Grain | `Live PSAdapter_plugin_Grn ` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_Grn ', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_Grn : XML applies it with defaults; dialog field 0 typed 41 -> descriptor Intn=41 read back) |
| Texture > Texturizer | `Live PSAdapter_plugin_Txtz` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_Txtz', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_Txtz: XML applies it with defaults; dialog field 0 typed 101 -> descriptor Scln=101 read back) |
| Texture > Craquelure | `Live PSAdapter_plugin_Crql` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_Crql', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_Crql: XML applies it with defaults; dialog field 0 typed 16 -> descriptor CrcS=16 read back) |
| Sketch > Note Paper | `Live PSAdapter_plugin_NtPr` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_NtPr', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_NtPr: XML applies it with defaults; dialog field 0 typed 26 -> descriptor ImgB=26 read back) |
| Sketch > Stamp | `Live PSAdapter_plugin_Stmp` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_Stmp', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_Stmp: XML applies it with defaults; dialog field 0 typed 26 -> descriptor LgDr=26 read back) |
| Sketch > Photocopy | `Live PSAdapter_plugin_Phtc` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_Phtc', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_Phtc: XML applies it with defaults; dialog field 0 typed 8 -> descriptor Drkn=8 read back) |
| Sketch > Water Paper | `Live PSAdapter_plugin_WtrP` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_WtrP', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_WtrP: XML applies it with defaults; dialog field 0 typed 16 -> descriptor FbrL=16 read back) |
| Sketch > Charcoal | `Live PSAdapter_plugin_Chrc` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_Chrc', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_Chrc: XML applies it with defaults; dialog field 0 typed 2 -> descriptor ChAm=2 read back) |
| Sketch > Graphic Pen | `Live PSAdapter_plugin_GraP` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_GraP', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_GraP: XML applies it with defaults; dialog field 0 typed 16 -> descriptor LgDr=16 read back) |
| Sketch > Plaster | `Live PSAdapter_plugin_Plst` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_Plst', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_Plst: XML applies it with defaults; dialog field 0 typed 21 -> descriptor ImgB=21 read back) |
| Sketch > Bas Relief | `Live PSAdapter_plugin_BsRl` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_BsRl', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_BsRl: XML applies it with defaults; dialog field 0 typed 14 -> descriptor Dtl =14 read back) |
| Sketch > Chalk & Charcoal | `Live PSAdapter_plugin_ChlC` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_ChlC', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_ChlC: XML applies it with defaults; dialog field 0 typed 7 -> descriptor ChrA=7 read back) |
| Sketch > Halftone Pattern | `Live PSAdapter_plugin_HlfS` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_HlfS', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_HlfS: XML applies it with defaults; dialog field 0 typed 2 -> descriptor HlSz=2 read back) |
| Sketch > Reticulation | `Live PSAdapter_plugin_Rtcl` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_Rtcl', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_Rtcl: XML applies it with defaults; dialog field 0 typed 13 -> descriptor Dnst=13 read back) |
| Sketch > Conté Crayon | `Live PSAdapter_plugin_CntC` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_CntC', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_CntC: XML applies it with defaults; dialog field 0 typed 12 -> descriptor FrgL=12 read back) |
| Sketch > Torn Edges | `Live PSAdapter_plugin_TrnE` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_TrnE', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_TrnE: XML applies it with defaults; dialog field 0 typed 26 -> descriptor ImgB=26 read back) |
| Sketch > Chrome | `Live PSAdapter_plugin_Chrm` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_Chrm', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_Chrm: XML applies it with defaults; dialog field 0 typed 5 -> descriptor Dtl =5 read back) |
| Artistic > Dry Brush | `Live PSAdapter_plugin_DryB` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_DryB', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_DryB: XML applies it with defaults; dialog field 0 typed 3 -> descriptor BrsS=3 read back) |
| Artistic > Plastic Wrap | `Live PSAdapter_plugin_PlsW` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_PlsW', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_PlsW: XML applies it with defaults; dialog field 0 typed 16 -> descriptor HghS=16 read back) |
| Artistic > Smudge Stick | `Live PSAdapter_plugin_SmdS` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_SmdS', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_SmdS: XML applies it with defaults; dialog field 0 typed 3 -> descriptor StrL=3 read back) |
| Artistic > Paint Daubs | `Live PSAdapter_plugin_PntD` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_PntD', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_PntD: XML applies it with defaults; dialog field 0 typed 9 -> descriptor Sz  =9 read back) |
| Artistic > Fresco | `Live PSAdapter_plugin_Frsc` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_Frsc', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_Frsc: XML applies it with defaults; dialog field 0 typed 3 -> descriptor BrsS=3 read back) |
| Artistic > Colored Pencil | `Live PSAdapter_plugin_ClrP` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_ClrP', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_ClrP: XML applies it with defaults; dialog field 0 typed 5 -> descriptor Pncl=5 read back) |
| Artistic > Cutout | `Live PSAdapter_plugin_Ct  ` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_Ct  ', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_Ct  : XML applies it with defaults; dialog field 0 typed 5 -> descriptor NmbL=5 read back) |
| Artistic > Watercolor | `Live PSAdapter_plugin_Wtrc` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_Wtrc', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_Wtrc: XML applies it with defaults; dialog field 0 typed 10 -> descriptor BrsD=10 read back) |
| Artistic > Poster Edges | `Live PSAdapter_plugin_PstE` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_PstE', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_PstE: XML applies it with defaults; dialog field 0 typed 3 -> descriptor EdgT=3 read back) |
| Artistic > Sponge | `Live PSAdapter_plugin_Spng` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_Spng', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_Spng: XML applies it with defaults; dialog field 0 typed 3 -> descriptor BrsS=3 read back) |
| Artistic > Film Grain | `Live PSAdapter_plugin_FlmG` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_FlmG', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_FlmG: XML applies it with defaults; dialog field 0 typed 5 -> descriptor Grn =5 read back) |
| Artistic > Rough Pastels | `Live PSAdapter_plugin_RghP` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_RghP', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_RghP: XML applies it with defaults; dialog field 0 typed 7 -> descriptor StrL=7 read back) |
| Artistic > Underpainting | `Live PSAdapter_plugin_Undr` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_Undr', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_Undr: XML applies it with defaults; dialog field 0 typed 7 -> descriptor BrsS=7 read back) |
| Artistic > Palette Knife | `Live PSAdapter_plugin_PltK` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_PltK', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_PltK: XML applies it with defaults; dialog field 0 typed 26 -> descriptor StrS=26 read back) |
| Artistic > Neon Glow | `Live PSAdapter_plugin_NGlw` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_NGlw', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_NGlw: XML applies it with defaults; dialog field 0 typed 6 -> descriptor Sz  =6 read back) |
| Video > NTSC Colors | `Live PSAdapter_plugin_NTSC` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_NTSC', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_NTSC: 1 params read back) |
| Video > De-Interlace | `Live PSAdapter_plugin_Dntr` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_Dntr', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_Dntr: applyEffect adds it with its defaults ({'IntE': 'ElmO', 'IntC': 'CrtI'}); no numeric dialog field to set) |
| Stylize > Glowing Edges | `Live PSAdapter_plugin_GlwE` | ✅ (effect readback) | AI.fx(item, 'PSAdapter_plugin_GlwE', {…}) = applyEffect(XML); menu command verified too (PSAdapter_plugin_GlwE: XML applies it with defaults; dialog field 0 typed 3 -> descriptor EdgW=3 read back) |

## View

| Command | executeMenuCommand | Status | How (script) |
|---|---|---|---|
| Outline / Preview | `preview` | ✅ (readback) | View > Outline (readback document.isOutlineMode()) |
| GPU Preview / Preview on CPU | `OpenGLCompositorPreview` | n/a | display-only toggle or preference (no document change, no readback) |
| Overprint Preview | `ink` | ✅ (readback) | View > Overprint Preview (readback document.getPreviewMode()) |
| Pixel Preview | `raster` | ✅ (readback) | View > Pixel Preview (readback document.getPreviewMode()) |
| Trim View | `TrimView` | ✅ (readback) | View > Trim View (readback document.isTrimViewEnabled()) — via the menu bar: 檢視 > 剪裁視圖 (tools/menu_ui.py; app.executeMenuCommand refuses this id) |
| Presentation Mode | `Adobe Presentation Mode` | n/a | display-only toggle or preference (no document change, no readback) |
| Proof Setup > Working CMYK | `proof-document` | n/a | display-only toggle or preference (no document change, no readback) |
| Proof Setup > Legacy Macintosh RGB | `proof-mac-rgb` | n/a | display-only toggle or preference (no document change, no readback) |
| Proof Setup > Internet Standard RGB (sRGB) | `proof-win-rgb` | n/a | display-only toggle or preference (no document change, no readback) |
| Proof Setup > Monitor RGB | `proof-monitor-rgb` | n/a | display-only toggle or preference (no document change, no readback) |
| Proof Setup > Color blindness - Protanopia-type | `proof-colorblindp` | n/a | display-only toggle or preference (no document change, no readback) |
| Proof Setup > Color blindness - Deuteranopia-type | `proof-colorblindd` | n/a | display-only toggle or preference (no document change, no readback) |
| Proof Setup > Customize | `proof-custom` | n/a | display-only toggle or preference (no document change, no readback) |
| Proof Colors | `proofColors` | n/a | display-only toggle or preference (no document change, no readback) |
| Zoom In | `zoomin` | ✅ (readback) | document.activeView.zoom |
| Zoom Out | `zoomout` | ✅ (readback) | document.activeView.zoom |
| Fit Artboard in Window | `fitin` | ✅ (readback) | document.activeView.zoom |
| Fit All in Window | `fitall` | ✅ (readback) | document.activeView.zoom |
| Rotate View > 180° | `RotateView180` | ✅ (readback) | document.activeView.rotateAngle = 180 (the menu needs GPU Preview) [menu ID refuses scripts: PARM] |
| Rotate View > 150° | `RotateView150` | ✅ (readback) | document.activeView.rotateAngle = 150 (the menu needs GPU Preview) [menu ID refuses scripts: PARM] |
| Rotate View > 135° | `RotateView135` | ✅ (readback) | document.activeView.rotateAngle = 135 (the menu needs GPU Preview) [menu ID refuses scripts: PARM] |
| Rotate View > 120° | `RotateView120` | ✅ (readback) | document.activeView.rotateAngle = 120 (the menu needs GPU Preview) [menu ID refuses scripts: PARM] |
| Rotate View > 90° | `RotateView90` | ✅ (readback) | document.activeView.rotateAngle = 90 (the menu needs GPU Preview) [menu ID refuses scripts: PARM] |
| Rotate View > 60° | `RotateView60` | ✅ (readback) | document.activeView.rotateAngle = 60 (the menu needs GPU Preview) [menu ID refuses scripts: PARM] |
| Rotate View > 45° | `RotateView45` | ✅ (readback) | document.activeView.rotateAngle = 45 (the menu needs GPU Preview) [menu ID refuses scripts: PARM] |
| Rotate View > 30° | `RotateView30` | ✅ (readback) | document.activeView.rotateAngle = 30 (the menu needs GPU Preview) [menu ID refuses scripts: PARM] |
| Rotate View > 15° | `RotateView15` | ✅ (readback) | document.activeView.rotateAngle = 15 (the menu needs GPU Preview) [menu ID refuses scripts: PARM] |
| Rotate View > 0° | `RotateViewZero` | ✅ (readback) | document.activeView.rotateAngle = 0 [menu ID refuses scripts: PARM] |
| Rotate View > -15° | `RotateViewNegative15` | ✅ (readback) | document.activeView.rotateAngle = -15 [menu ID refuses scripts: PARM] |
| Rotate View > -30° | `RotateViewNegative30` | ✅ (readback) | document.activeView.rotateAngle = -30 [menu ID refuses scripts: PARM] |
| Rotate View > -45° | `RotateViewNegative45` | ✅ (readback) | document.activeView.rotateAngle = -45 [menu ID refuses scripts: PARM] |
| Rotate View > -60° | `RotateViewNegative60` | ✅ (readback) | document.activeView.rotateAngle = -60 [menu ID refuses scripts: PARM] |
| Rotate View > -90° | `RotateViewNegative90` | ✅ (readback) | document.activeView.rotateAngle = -90 [menu ID refuses scripts: PARM] |
| Rotate View > -120° | `RotateViewNegative120` | ✅ (readback) | document.activeView.rotateAngle = -120 [menu ID refuses scripts: PARM] |
| Rotate View > -135° | `RotateViewNegative135` | ✅ (readback) | document.activeView.rotateAngle = -135 [menu ID refuses scripts: PARM] |
| Rotate View > -150° | `RotateViewNegative150` | ✅ (readback) | document.activeView.rotateAngle = -150 [menu ID refuses scripts: PARM] |
| Rotate View > -180° | `RotateViewNegative180` | ✅ (readback) | document.activeView.rotateAngle = -180 [menu ID refuses scripts: PARM] |
| Reset Rotate View | `resetRotationView` | ✅ (readback) | document.activeView.rotateAngle = 0 [menu ID refuses scripts: PARM] |
| Rotate View to Selection | `rotateViewToSelection` | ✅ (readback) | document.activeView.rotateAngle = the item's rotation (30 deg here) [menu ID refuses scripts: PARM] |
| Hide Slices | `AISlice Feedback Menu` | n/a | display-only toggle or preference (no document change, no readback) |
| Lock Slices | `AISlice Lock Menu` | n/a | display-only toggle or preference (no document change, no readback) |
| Hide Bounding Box | `AI Bounding Box Toggle` | n/a | display-only toggle or preference (no document change, no readback) |
| Show Transparency Grid | `TransparencyGrid Menu Item` | ✅ (readback) | View > Transparency Grid (readback document.isTransparencyGridVisible()) |
| Actual Size | `actualsize` | ✅ (readback) | view.visibleZoom reads 1 (view.zoom is scaled by the display DPI: 1.5 at 150%) |
| Hide Gradient Annotator | `Gradient Feedback` | n/a | display-only toggle or preference (no document change, no readback) |
| Show Live Paint Gaps | `Show Gaps Planet X` | n/a | display-only toggle or preference (no document change, no readback) |
| Hide Corner Widget | `Live Corner Annotator` | n/a | display-only toggle or preference (no document change, no readback) |
| Hide Edges | `edge` | n/a | display-only toggle or preference (no document change, no readback) |
| Smart Guides | `Snapomatic on-off menu item` | n/a | display-only toggle or preference (no document change, no readback) |
| Perspective Grid > Show Grid | `Show Perspective Grid` | ✅ (deep) | document.showPerspectiveGrid() / hidePerspectiveGrid() |
| Perspective Grid > Show Rulers | `Show Ruler` | n/a | perspective grid display / preset settings |
| Perspective Grid > Snap to Grid | `Snap to Grid` | n/a | perspective grid display / preset settings |
| Perspective Grid > Lock Grid | `Lock Perspective Grid` | n/a | perspective grid display / preset settings |
| Perspective Grid > Lock Station Point | `Lock Station Point` | n/a | perspective grid display / preset settings |
| Perspective Grid > Define Grid | `Define Perspective Grid` | n/a | perspective grid display / preset settings |
| Perspective Grid > Save Grid as Preset | `Save Perspective Grid as Preset` | n/a | perspective grid display / preset settings |
| Hide Artboards | `artboard` | n/a | display-only toggle or preference (no document change, no readback) |
| Show Print Tiling | `pagetiling` | n/a | display-only toggle or preference (no document change, no readback) |
| Show Template | `showtemplate` | n/a | display-only toggle or preference (no document change, no readback) |
| Rulers > Show Rulers | `ruler` | ✅ (readback) | View > Rulers (readback document.isRulerVisible()) |
| Rulers > Change to Global Rulers | `rulerCoordinateSystem` | n/a | display-only toggle or preference (no document change, no readback) |
| Rulers > Show Video Rulers | `videoruler` | n/a | display-only toggle or preference (no document change, no readback) |
| Show Text Threads | `textthreads` | n/a | display-only toggle or preference (no document change, no readback) |
| Guides > Hide Guides | `showguide` | ✅ (readback) | View > Guides (readback document.isGuideVisible()) |
| Guides > Lock Guides | `lockguide` | ✅ (menu readback) | View > Guides > Lock Guides (readback: the Guides menu switches between Lock and Unlock Guides) |
| Guides > Make Guides | `makeguide` | ✅ (readback) | pathItem.guides = true |
| Guides > Release Guides | `releaseguide` | ✅ (readback) | pathItem.guides = false |
| Guides > Clear Guides | `clearguide` | ✅ (readback) | remove every pathItem with guides == true |
| Show Grid | `showgrid` | ✅ (readback) | View > Show Grid (readback document.isGridVisible()) |
| Snap to Grid | `snapgrid` | n/a | display-only toggle or preference (no document change, no readback) |
| Snap to Pixel | `pixelconstraints` | n/a | display-only toggle or preference (no document change, no readback) |
| Snap to Point | `snappoint` | n/a | display-only toggle or preference (no document change, no readback) |
| Snap to Glyph | `glyphSnapping` | n/a | display-only toggle or preference (no document change, no readback) |
| New View | `newview` | ✅ (deep) | View > New View (name typed) |
| Edit Views | `editview` | n/a | display-only toggle or preference (no document change, no readback) |
| Saved View 1 | `view1` | n/a | display-only toggle or preference (no document change, no readback) |
| Saved View 2 | `view2` | n/a | display-only toggle or preference (no document change, no readback) |
| Saved View 3 | `view3` | n/a | display-only toggle or preference (no document change, no readback) |
| Saved View 4 | `view4` | n/a | display-only toggle or preference (no document change, no readback) |
| Saved View 5 | `view5` | n/a | display-only toggle or preference (no document change, no readback) |
| Saved View 6 | `view6` | n/a | display-only toggle or preference (no document change, no readback) |
| Saved View 7 | `view7` | n/a | display-only toggle or preference (no document change, no readback) |
| Saved View 8 | `view8` | n/a | display-only toggle or preference (no document change, no readback) |
| Saved View 9 | `view9` | n/a | display-only toggle or preference (no document change, no readback) |
| Saved View 10 | `view10` | n/a | display-only toggle or preference (no document change, no readback) |

## Window

| Command | executeMenuCommand | Status | How (script) |
|---|---|---|---|
| New Window | `newwindow` | ✅ (readback) | Window > New Window (readback document.views.length) |
| Arrange > Cascade | `cascade` | n/a | panel / workspace / toolbar UI |
| Arrange > Tile | `tile` | n/a | panel / workspace / toolbar UI |
| Arrange > Float in Window | `floatInWindow` | n/a | panel / workspace / toolbar UI |
| Arrange > Float All in Windows | `floatAllInWindows` | n/a | panel / workspace / toolbar UI |
| Arrange > Consolidate All Windows | `consolidateAllWindows` | n/a | panel / workspace / toolbar UI |
| Find Extensions on Exchange | `Browse Add-Ons Menu` | n/a | panel / workspace / toolbar UI |
| Workspace > Touch | `Adobe Touch Workspace` | n/a | panel / workspace / toolbar UI |
| Workspace > Reset | `Adobe Reset Workspace` | n/a | panel / workspace / toolbar UI |
| Workspace > New Workspace | `Adobe New Workspace` | n/a | panel / workspace / toolbar UI |
| Workspace > Manage Workspaces | `Adobe Manage Workspace` | n/a | panel / workspace / toolbar UI |
| Toolbars > Basic | `Adobe Basic Toolbar Menu` | n/a | panel / workspace / toolbar UI |
| Toolbars > Advanced | `Adobe Advanced Toolbar Menu` | n/a | panel / workspace / toolbar UI |
| Toolbars > New Toolbar | `New Tools Panel` | n/a | panel / workspace / toolbar UI |
| Toolbars > Manage Toolbar | `Manage Tools Panel` | n/a | panel / workspace / toolbar UI |
| Control | `drover control palette plugin` | n/a | panel / workspace / toolbar UI |
| 3D and Materials | `Adobe 3D Panel` | n/a | panel / workspace / toolbar UI |
| CSS Properties | `CSS Menu Item` | n/a | panel / workspace / toolbar UI |
| Retype (Beta) | `ReTypeWindowMenu` | n/a | panel / workspace / toolbar UI |
| SVG Interactivity | `Adobe SVG Interactivity Palette` | n/a | panel / workspace / toolbar UI |
| Generate Patterns (Beta) | `Generate` | n/a | panel / workspace / toolbar UI |
| Properties | `Adobe Property Palette` | n/a | panel / workspace / toolbar UI |
| Separations Preview | `Adobe Separation Preview Panel` | n/a | panel / workspace / toolbar UI |
| Actions | `Adobe Action Palette` | n/a | panel / workspace / toolbar UI |
| Layers | `AdobeLayerPalette1` | n/a | panel / workspace / toolbar UI |
| Pattern Options | `Adobe Pattern Panel Toggle` | n/a | panel / workspace / toolbar UI |
| Asset Export | `Style Palette` | n/a | panel / workspace / toolbar UI |
| Align | `AdobeAlignObjects2` | n/a | panel / workspace / toolbar UI |
| Navigator | `AdobeNavigator` | n/a | panel / workspace / toolbar UI |
| Attributes | `internal palettes posing as plug-in menus-attributes` | n/a | panel / workspace / toolbar UI |
| Artboards | `Adobe Artboard Palette` | n/a | panel / workspace / toolbar UI |
| Flattener Preview | `Adobe Flattening Preview` | n/a | panel / workspace / toolbar UI |
| Image Trace | `Adobe Vectorize Panel` | n/a | panel / workspace / toolbar UI |
| Document Info | `DocInfo1` | n/a | panel / workspace / toolbar UI |
| Type > OpenType | `internal palettes posing as plug-in menus-opentype` | n/a | panel / workspace / toolbar UI |
| Type > Character | `internal palettes posing as plug-in menus-character` | n/a | panel / workspace / toolbar UI |
| Type > Character Styles | `Character Styles` | n/a | panel / workspace / toolbar UI |
| Type > Glyphs | `alternate glyph palette plugin 2` | n/a | panel / workspace / toolbar UI |
| Type > Tabs | `internal palettes posing as plug-in menus-tab` | n/a | panel / workspace / toolbar UI |
| Type > Paragraph | `internal palettes posing as plug-in menus-paragraph` | n/a | panel / workspace / toolbar UI |
| Type > Paragraph Styles | `Adobe Paragraph Styles Palette` | n/a | panel / workspace / toolbar UI |
| Mockup (Beta) | `Adobe Vector Edge Panel` | n/a | panel / workspace / toolbar UI |
| History | `Adobe History Panel Menu Item` | n/a | panel / workspace / toolbar UI |
| Gradient | `Adobe Gradient Palette` | n/a | panel / workspace / toolbar UI |
| Symbols | `Adobe Symbol Palette` | n/a | panel / workspace / toolbar UI |
| Brushes | `Adobe BrushManager Menu Item` | n/a | panel / workspace / toolbar UI |
| Stroke | `Adobe Stroke Palette` | n/a | panel / workspace / toolbar UI |
| Graphic Styles | `Adobe Style Palette` | n/a | panel / workspace / toolbar UI |
| Color Guide | `Adobe Harmony Palette` | n/a | panel / workspace / toolbar UI |
| Swatches | `Adobe Swatches Menu Item` | n/a | panel / workspace / toolbar UI |
| Transform | `AdobeTransformObjects1` | n/a | panel / workspace / toolbar UI |
| Variables | `Adobe Variables Palette Menu Item` | n/a | panel / workspace / toolbar UI |
| Libraries | `Adobe CSXS Extension com.adobe.DesignLibraries.angular\750\663\607\746\626\631\745\672\653` | n/a | panel / workspace / toolbar UI |
| Asset Export | `Adobe SmartExport Panel Menu Item` | n/a | panel / workspace / toolbar UI |
| Info | `internal palettes posing as plug-in menus-info` | n/a | panel / workspace / toolbar UI |
| Pathfinder | `Adobe PathfinderUI` | n/a | panel / workspace / toolbar UI |
| Transparency | `Adobe Transparency Palette Menu Item` | n/a | panel / workspace / toolbar UI |
| Links | `Adobe LinkPalette Menu Item` | n/a | panel / workspace / toolbar UI |
| Color | `Adobe Color Palette` | n/a | panel / workspace / toolbar UI |
| Magic Wand | `AI Magic Wand` | n/a | panel / workspace / toolbar UI |
| Symbol Libraries > Other Library | `Adobe Symbol Palette Plugin Other libraries menu item` | n/a | panel / workspace / toolbar UI |
| Brush Libraries > Other Library | `AdobeBrushMgrUI Other libraries menu item` | n/a | panel / workspace / toolbar UI |
| Graphic Style Libraries > Other Library | `Adobe Art Style Plugin Other libraries menu item` | n/a | panel / workspace / toolbar UI |
| Swatch Libraries > Other Library | `AdobeSwatch_ Other libraries menu item` | n/a | panel / workspace / toolbar UI |

## Help

| Command | executeMenuCommand | Status | How (script) |
|---|---|---|---|
| Illustrator Help | `helpcontent` | n/a | help, web pages, bug report |
| Support Center | `supportContent` | n/a | help, web pages, bug report |
| What's New | `whatsNewContent` | n/a | help, web pages, bug report |
| Community | `supportCommunity` | n/a | help, web pages, bug report |
| Submit Bug/Feature Request | `wishform` | n/a | help, web pages, bug report |
| System Info | `systemInfo` | n/a | help, web pages, bug report |
| About Illustrator | `about` | n/a | help, web pages, bug report |

## Keyboard

| Command | executeMenuCommand | Status | How (script) |
|---|---|---|---|
| Switch Selection Tools | `switchSelTool` | n/a | keyboard navigation / duplicate shortcut / UI toggle |
| Font Size Up (large step) | `faceSizeUp` | ✅ (readback) | characterAttributes.size += 10 (large step) [menu ID refuses scripts: PARM] |
| Font Size Down (large step) | `faceSizeDown` | ✅ (readback) | characterAttributes.size -= 10 [menu ID refuses scripts: PARM] |
| Font Size Up | `sizeStepUp` | ✅ (readback) | characterAttributes.size += 2 (the shortcut step) [menu ID refuses scripts: PARM] |
| Font Size Down | `sizeStepDown` | ✅ (readback) | characterAttributes.size -= 2 [menu ID refuses scripts: PARM] |
| Kern/Track Looser | `~kernFurther` | ✅ (readback) | characterAttributes.tracking += 20 [menu ID refuses scripts: PARM] |
| Kern/Track Tighter | `~kernCloser` | ✅ (readback) | characterAttributes.tracking -= 20 [menu ID refuses scripts: PARM] |
| Tracking Looser (word) | `tracking` | ✅ (readback) | characterAttributes.tracking += 100 (word step) [menu ID refuses scripts: PARM] |
| Clear Tracking | `clearTrack` | ✅ (readback) | characterAttributes.tracking = 0 [menu ID refuses scripts: PARM] |
| Word Spacing | `spacing` | ✅ (readback) | paragraphAttributes.desiredWordSpacing [menu ID refuses scripts: PARM] |
| Reset Horizontal/Vertical Scale | `clearTypeScale` | ✅ (readback) | characterAttributes.horizontalScale = verticalScale = 100 [menu ID refuses scripts: PARM] |
| Highlight Font | `highlightFont` | n/a | keyboard navigation / duplicate shortcut / UI toggle |
| Highlight Font (alt) | `highlightFont2` | n/a | keyboard navigation / duplicate shortcut / UI toggle |
| Align Text Left | `leftAlign` | ✅ (readback) | paragraphAttributes.justification = Justification.LEFT [menu ID refuses scripts: PARM] |
| Align Text Center | `centerAlign` | ✅ (readback) | paragraphAttributes.justification = Justification.CENTER [menu ID refuses scripts: PARM] |
| Align Text Right | `rightAlign` | ✅ (readback) | paragraphAttributes.justification = Justification.RIGHT [menu ID refuses scripts: PARM] |
| Justify Left | `justify` | ✅ (readback) | paragraphAttributes.justification = Justification.FULLJUSTIFYLASTLINELEFT [menu ID refuses scripts: PARM] |
| Justify Center | `justifyCenter` | ✅ (readback) | paragraphAttributes.justification = Justification.FULLJUSTIFYLASTLINECENTER [menu ID refuses scripts: PARM] |
| Justify Right | `justifyRight` | ✅ (readback) | paragraphAttributes.justification = Justification.FULLJUSTIFYLASTLINERIGHT [menu ID refuses scripts: PARM] |
| Justify All Lines | `justifyAll` | ✅ (readback) | paragraphAttributes.justification = Justification.FULLJUSTIFY [menu ID refuses scripts: PARM] |
| Toggle Auto Hyphenation | `toggleAutoHyphen` | ✅ (readback) | paragraphAttributes.hyphenation = !hyphenation [menu ID refuses scripts: PARM] |
| Toggle Line Composer | `toggleLineComposer` | ✅ (readback) | paragraphAttributes.everyLineComposer = !everyLineComposer [menu ID refuses scripts: PARM] |
| Subscript | `~subscript` | ✅ (readback) | characterAttributes.baselinePosition = FontBaselineOption.SUBSCRIPT [menu ID refuses scripts: PARM] |
| Superscript | `~superScript` | ✅ (readback) | characterAttributes.baselinePosition = FontBaselineOption.SUPERSCRIPT [menu ID refuses scripts: PARM] |
| Lock Unselected Artwork | `lock2` | ✅ (readback) | lock every unselected item: item.locked = true where !item.selected [menu ID refuses scripts: PARM] |
| Hide Unselected Artwork | `hide2` | ✅ (readback) | hide every unselected item: item.hidden = true where !item.selected [menu ID refuses scripts: PARM] |
| Repeat Pathfinder | `repeatPathfinder` | ✅ (readback) | call AI.pathfinder(items, op) again (repeat Pathfinder) [menu ID refuses scripts: PARM] |
| Average and Join | `avgAndJoin` | ✅ (readback) | MENU('average') + MENU('join') on the two end points [menu ID refuses scripts: PARM] |
| Enter Isolation Mode | `enterFocus` | ✅ (readback) | double-click the group with the Selection tool (tools/menu_ui.dblclick_color); readback: the temporary Isolation Mode layer appears |
| Exit Isolation Mode | `exitFocus` | ✅ (readback) | Esc in the document window leaves isolation mode (readback: the Isolation Mode layer is gone) |
| New Symbol | `Adobe New Symbol Shortcut` | ✅ (readback) | document.symbols.add(item) |
| Cycle Color Modes | `Adobe Color Palette Secondary` | n/a | keyboard navigation / duplicate shortcut / UI toggle |
| Actions Batch | `Adobe Actions Batch` | n/a | keyboard navigation / duplicate shortcut / UI toggle |
| Add New Fill | `Adobe New Fill Shortcut` | ✅ (deep) | Appearance: add new fill |
| Add New Stroke | `Adobe New Stroke Shortcut` | ✅ (deep) | Appearance: add new stroke |
| New Graphic Style | `Adobe New Style Shortcut` | ✅ (readback) | Graphic Styles: new style from selection |
| New Layer | `AdobeLayerPalette2` | ✅ (readback) | document.layers.add() |
| New Layer with Options | `AdobeLayerPalette3` | ✅ (readback) | document.layers.add() (+ options dialog) |
| Update Link | `Adobe Update Link Shortcut` | ✅ (readback) | placedItem.relink(file) / update after the file changed |
| New Swatch | `Adobe New Swatch Shortcut Menu` | ✅ (readback) | document.swatches.add() |
| Debug Panel | `Debug Panel` | n/a | keyboard navigation / duplicate shortcut / UI toggle |
| Cycle Units | `switchUnits` | n/a | keyboard navigation / duplicate shortcut / UI toggle |
| New (alternate) | `new2` | n/a | keyboard navigation / duplicate shortcut / UI toggle |
| Close All (alternate) | `closeAll2` | n/a | keyboard navigation / duplicate shortcut / UI toggle |
| Help (alternate) | `helpcontent2` | n/a | keyboard navigation / duplicate shortcut / UI toggle |
| Undo (alternate) | `undo2` | n/a | keyboard navigation / duplicate shortcut / UI toggle |
| Cut (alternate) | `cut2` | n/a | keyboard navigation / duplicate shortcut / UI toggle |
| Copy (alternate) | `copy2` | n/a | keyboard navigation / duplicate shortcut / UI toggle |
| Paste (alternate) | `paste2` | n/a | keyboard navigation / duplicate shortcut / UI toggle |
| Zoom In (alternate) | `zoomin2` | n/a | keyboard navigation / duplicate shortcut / UI toggle |
| Debug Palette | `debugPalette` | n/a | keyboard navigation / duplicate shortcut / UI toggle |
| Next Document | `navigateToNextDocument` | n/a | keyboard navigation / duplicate shortcut / UI toggle |
| Previous Document | `navigateToPreviousDocument` | n/a | keyboard navigation / duplicate shortcut / UI toggle |
| Next Document Group | `navigateToNextDocumentGroup` | n/a | keyboard navigation / duplicate shortcut / UI toggle |
| Previous Document Group | `navigateToPreviousDocumentGroup` | n/a | keyboard navigation / duplicate shortcut / UI toggle |
| Subscript (alternate) | `~subscript2` | n/a | keyboard navigation / duplicate shortcut / UI toggle |
| Superscript (alternate) | `~superScript2` | n/a | keyboard navigation / duplicate shortcut / UI toggle |

## Tools

60/85 tools activated by `app.selectTool(name)` and read back with `app.getSelectedToolName()`. The "script equivalent" column is how to get the tool's result without the mouse.

| Tool | selectTool | Script equivalent |
|---|---|---|
| `Adobe Select Tool` | accepted (Illustrator's getSelectedToolName() throws PARM for this tool) | document.selection = items / AI.select() |
| `Adobe Direct Select Tool` | accepted (Illustrator's getSelectedToolName() throws PARM for this tool) | pathPoint.selected = PathPointSelection.ANCHORPOINT |
| `Adobe Direct Object Select Tool` | accepted (Illustrator's getSelectedToolName() throws PARM for this tool) | select an item inside a group: group.pageItems[i].selected = true |
| `Adobe Magic Wand Tool` | ✅ read back | Select > Same > … (menu sweep) |
| `Adobe Crop Tool` | ✅ read back | artboards: AI.addArtboard() / artboard.artboardRect |
| `Adobe Direct Lasso Tool` | ✅ read back | pathPoint.selected by region (loop points inside a polygon) |
| `Adobe Pen Tool` | accepted (Illustrator's getSelectedToolName() throws PARM for this tool) | AI.path(points) / pathItem.setEntirePath() + pathPoints[i].leftDirection/rightDirection |
| `Adobe Add Anchor Point Tool` | accepted (Illustrator's getSelectedToolName() throws PARM for this tool) | Object > Path > Add Anchor Points / pathPoints.add() |
| `Adobe Delete Anchor Point Tool` | accepted (Illustrator's getSelectedToolName() throws PARM for this tool) | pathPoint.remove() |
| `Adobe Anchor Point Tool` | accepted (Illustrator's getSelectedToolName() throws PARM for this tool) | pathPoint.pointType = PointType.SMOOTH / CORNER |
| `Adobe Curvature Tool` | ✅ read back | AI.path([[x, y, inX, inY, outX, outY], …]) smooth points |
| `Adobe Line Tool` | ✅ read back | AI.line(x1, y1, x2, y2) |
| `Adobe Arc Tool` | ✅ read back | AI.path with bezier handles (quarter arc) |
| `Adobe Shape Construction Spiral Tool` | ✅ read back | AI.path with computed spiral points |
| `Adobe Rectangular Grid Tool` | ✅ read back | loops of AI.line / AI.grid |
| `Adobe Polar Grid Tool` | ✅ read back | AI.circle rings + AI.line spokes |
| `Adobe Rectangle Shape Tool` | ✅ read back | AI.rect() |
| `Adobe Rounded Rectangle Tool` | ✅ read back | AI.roundRect() |
| `Adobe Ellipse Shape Tool` | ✅ read back | AI.ellipse() / AI.circle() |
| `Adobe Shape Construction Regular Polygon Tool` | ✅ read back | AI.polygon() |
| `Adobe Shape Construction Star Tool` | ✅ read back | AI.star() |
| `Adobe Flare Tool` | ✅ read back | Flare needs a mouse gesture (no DOM) |
| `Adobe Brush Tool` | ✅ read back | brush.applyTo(path) |
| `Adobe Blob Brush Tool` | ✅ read back | filled paths: AI.path + Pathfinder unite |
| `Adobe Freehand Tool` | ✅ read back | AI.path(points) (pencil) |
| `Adobe Freehand Smooth Tool` | ✅ read back | Object > Path > Smooth |
| `Adobe Freehand Erase Tool` | ✅ read back | pathPoint.remove() / Pathfinder minusFront |
| `Adobe Shaper Tool` | ✅ read back | AI.rect/AI.ellipse/AI.polygon + AI.pathfinder |
| `Adobe Symbol Sprayer Tool` | ✅ read back | loop symbolItems.add(symbol) at positions |
| `Adobe Symbol Shifter Tool` | ✅ read back | symbolItem.translate() |
| `Adobe Symbol Scruncher Tool` | ✅ read back | symbolItem.translate() |
| `Adobe Symbol Sizer Tool` | ✅ read back | symbolItem.resize() |
| `Adobe Symbol Spinner Tool` | ✅ read back | symbolItem.rotate() |
| `Adobe Symbol Stainer Tool` | ✅ read back | symbolItem colorize via opacity/blend |
| `Adobe Symbol Screener Tool` | ✅ read back | symbolItem.opacity |
| `Adobe Symbol Styler Tool` | ✅ read back | graphicStyle.applyTo(symbolItem) |
| `Adobe Column Graph Tool` | accepted (Illustrator's getSelectedToolName() throws PARM for this tool) | graphs cannot be created by script (tests/fixtures/graph.ai made with the tool) |
| `Adobe Stacked Column Graph Tool` | accepted (Illustrator's getSelectedToolName() throws PARM for this tool) | graph (fixture) |
| `Adobe Bar Graph Tool` | accepted (Illustrator's getSelectedToolName() throws PARM for this tool) | graph (fixture) |
| `Adobe Stacked Bar Graph Tool` | accepted (Illustrator's getSelectedToolName() throws PARM for this tool) | graph (fixture) |
| `Adobe Line Graph Tool` | accepted (Illustrator's getSelectedToolName() throws PARM for this tool) | graph (fixture) |
| `Adobe Area Graph Tool` | accepted (Illustrator's getSelectedToolName() throws PARM for this tool) | graph (fixture) |
| `Adobe Scatter Graph Tool` | accepted (Illustrator's getSelectedToolName() throws PARM for this tool) | graph (fixture) |
| `Adobe Pie Graph Tool` | accepted (Illustrator's getSelectedToolName() throws PARM for this tool) | graph (fixture) |
| `Adobe Radar Graph Tool` | accepted (Illustrator's getSelectedToolName() throws PARM for this tool) | graph (fixture) |
| `Adobe Slice Tool` | ✅ read back | item.sliced = true / Object > Slice |
| `Adobe Slice Select Tool` | ✅ read back | select sliced items |
| `Perspective Grid Tool` | ✅ read back | document.showPerspectiveGrid() |
| `Perspective Selection Tool` | ✅ read back | Object > Perspective > Attach to Active Plane |
| `Adobe Type Tool` | ✅ read back | AI.text(str, x, y, {…}) (point text) |
| `Adobe Area Type Tool` | ✅ read back | AI.text(str, x, y, {width, height}) (area text) |
| `Adobe Path Type Tool` | ✅ read back | AI.textOnPath(path, str) |
| `Adobe Vertical Type Tool` | ✅ read back | AI.text(str, x, y, {vertical: true}) |
| `Adobe Vertical Area Type Tool` | ✅ read back | areaText + orientation VERTICAL |
| `Adobe Vertical Path Type Tool` | ✅ read back | pathText + orientation VERTICAL |
| `Adobe Touch Type Tool` | ✅ read back | characters[i].characterAttributes (size, rotation, baselineShift, horizontalScale) |
| `Adobe Gradient Vector Tool` | ✅ read back | AI.gradient() fill + GradientColor.angle / origin |
| `Adobe Mesh Editing Tool` | ✅ read back | Object > Create Gradient Mesh (menu sweep) |
| `Adobe Shape Builder Tool` | ✅ read back | AI.pathfinder(items, 'unite' / 'divide' …) |
| `Adobe Planar Paintbucket Tool` | ✅ read back | Live Paint (menu sweep); fill via pathfinder divide + fillColor |
| `Adobe Planar Face Select Tool` | ✅ read back | Live Paint selection |
| `Adobe Rotate Tool` | accepted (Illustrator's getSelectedToolName() throws PARM for this tool) | AI.rotate() |
| `Adobe Reflect Tool` | accepted (Illustrator's getSelectedToolName() throws PARM for this tool) | AI.flip() |
| `Adobe Scale Tool` | accepted (Illustrator's getSelectedToolName() throws PARM for this tool) | AI.scaleTo() / item.resize() |
| `Adobe Shear Tool` | accepted (Illustrator's getSelectedToolName() throws PARM for this tool) | item.transform(shear matrix) |
| `Adobe Reshape Tool` | ✅ read back | move pathPoints[i].anchor |
| `Adobe Width Tool` | ✅ read back | variable width profile (no DOM; use stroke + Offset Path) |
| `Adobe Warp Tool` | ✅ read back | AI.warp() / Envelope Distort |
| `Adobe New Twirl Tool` | ✅ read back | Effect > Distort & Transform > Twist (AI.fx) |
| `Adobe Pucker Tool` | ✅ read back | Effect > Pucker & Bloat (AI.fx) |
| `Adobe Bloat Tool` | ✅ read back | Effect > Pucker & Bloat (AI.fx) |
| `Adobe Scallop Tool` | ✅ read back | Effect > Zig Zag / Roughen (AI.fx) |
| `Adobe Cyrstallize Tool` | ✅ read back | Effect > Roughen (AI.fx) |
| `Adobe Wrinkle Tool` | ✅ read back | Effect > Roughen (AI.fx) |
| `Adobe Free Transform Tool` | ✅ read back | item.transform(matrix) / Effect > Free Distort |
| `Adobe Measure Tool` | accepted (Illustrator's getSelectedToolName() throws PARM for this tool) | AI.box(item) (readback) |
| `Adobe Eyedropper Tool` | ✅ read back | copy colors: target.fillColor = source.fillColor |
| `Adobe Blend Tool` | ✅ read back | AI.blend() |
| `Adobe Eraser Tool` | ✅ read back | Pathfinder minusFront with an eraser shape |
| `Adobe Scissors Tool` | accepted (Illustrator's getSelectedToolName() throws PARM for this tool) | split a path: two AI.path() from its points |
| `Adobe Knife Tool` | ✅ read back | Object > Path > Divide Objects Below |
| `Adobe Scroll Tool` | accepted (Illustrator's getSelectedToolName() throws PARM for this tool) | view: document.activeView.centerPoint |
| `Adobe Page Tool` | accepted (Illustrator's getSelectedToolName() throws PARM for this tool) | print tiling (no DOM) |
| `Adobe Rotate Canvas Tool` | ✅ read back | document.activeView.rotateAngle |
| `Adobe Zoom Tool` | accepted (Illustrator's getSelectedToolName() throws PARM for this tool) | document.activeView.zoom |

The shortcut set also lists 0 tool-context shortcuts (blend-mode / opacity / paint / fill-stroke keys). Their effect is set directly: item.blendingMode, item.opacity, fillColor / strokeColor (tested in tests/REPORT.md, style).

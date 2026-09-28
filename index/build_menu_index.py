"""Illustrator's complete menu-command inventory, taken from YOUR Illustrator.

Illustrator has no scriptable menu tree (Photoshop has menuBarInfo; Illustrator does not). But Edit > Keyboard
Shortcuts can Save a set: the saved .kys lists the internal name of every menu command in menu order, and those
names are exactly the strings app.executeMenuCommand() takes. "Export Text" in the same dialog writes the
localized menu labels in the same order.
  index/raw/ai2024_commands.kys   saved from Illustrator 28.0 (python tools/capture_commands.py captures it from yours)
  index/raw/shortcuts_<locale>.txt   the localized menu as Illustrator exports it (reference only)
This script gives every command its English menu path (table below, in menu order) and writes
index/menu-index.json: [{cmd, path, top, key, mods}]
Usage: python index/build_menu_index.py
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
RAW = HERE / "raw"


def parse_kys(p):
    t = p.read_text(encoding="utf-8", errors="replace")
    depth, cur, out, key = 0, None, {}, {}
    name = None
    for line in t.splitlines():
        s = line.strip()
        m = re.match(r"^/(.+?) \{$", s)
        if m:
            if depth == 0:
                cur = m.group(1)
                out[cur] = []
            elif depth == 1:
                name = m.group(1).replace("\\ ", " ")
                out[cur].append(name)
            depth += 1
        elif s == "}":
            depth -= 1
        elif depth == 2 and name:
            km = re.match(r"^/(Key|Modifiers) (\d+)", s)
            if km:
                key.setdefault((cur, name), {})[km.group(1)] = int(km.group(2))
    return out, key


# English menu path for every command (menu order). "Keyboard >" = shortcut-only commands with no menu item.
P = {}


def sec(prefix, pairs):
    for cmd, label in pairs:
        P[cmd] = f"{prefix} > {label}" if prefix else label


sec("File", [("new", "New"), ("newFromTemplate", "New from Template"), ("open", "Open"), ("Adobe Bridge Browse", "Browse in Bridge"),
             ("close", "Close"), ("closeAll", "Close All"), ("save", "Save"), ("saveas", "Save As"), ("saveacopy", "Save a Copy"),
             ("Adobe AI Save Selected Slices", "Save Selected Slices"), ("saveasTemplate", "Save as Template"), ("revert", "Revert"),
             ("Search Adobe Stock", "Search Adobe Stock"), ("AI Place", "Place"), ("exportForScreens", "Export > Export for Screens"),
             ("export", "Export > Export As"), ("Adobe AI Save For Web", "Export > Save for Web (Legacy)"), ("exportSelection", "Export Selection"),
             ("Package Menu Item", "Package"), ("ai_browse_for_script", "Scripts > Other Script"), ("document", "Document Setup"),
             ("doc-color-cmyk", "Document Color Mode > CMYK Color"), ("doc-color-rgb", "Document Color Mode > RGB Color"), ("File Info", "File Info"),
             ("Print", "Print"), ("quit", "Exit")])
sec("Edit", [("undo", "Undo"), ("redo", "Redo"), ("cut", "Cut"), ("copy", "Copy"), ("paste", "Paste"), ("pasteFront", "Paste in Front"),
             ("pasteBack", "Paste in Back"), ("pasteInPlace", "Paste in Place"), ("pasteInAllArtboard", "Paste on All Artboards"),
             ("pasteWithoutFormatting", "Paste without Formatting"), ("clear", "Clear"), ("Find and Replace", "Find and Replace"), ("Find Next", "Find Next"),
             ("Auto Spell Check", "Spelling > Auto Spell Check"), ("Check Spelling", "Spelling > Check Spelling"), ("Edit Custom Dictionary...", "Edit Custom Dictionary"),
             ("Recolor Art Dialog", "Edit Colors > Recolor Artwork"), ("Generative Recolor Art Dialog", "Edit Colors > Generative Recolor"),
             ("Colors6", "Edit Colors > Invert Colors"), ("Colors5", "Edit Colors > Blend Vertically"), ("Colors4", "Edit Colors > Blend Horizontally"),
             ("Colors3", "Edit Colors > Blend Front to Back"), ("Adjust3", "Edit Colors > Adjust Color Balance"), ("Colors8", "Edit Colors > Convert to CMYK"),
             ("Colors9", "Edit Colors > Convert to RGB"), ("Colors7", "Edit Colors > Convert to Grayscale"), ("Saturate3", "Edit Colors > Saturate"),
             ("Overprint2", "Edit Colors > Overprint Black"), ("EditOriginal Menu Item", "Edit Original"), ("Transparency Presets", "Transparency Flattener Presets"),
             ("Print Presets", "Print Presets"), ("PDF Presets", "Adobe PDF Presets"), ("PerspectiveGridPresets", "Perspective Grid Presets"),
             ("color", "Color Settings"), ("assignprofile", "Assign Profile"), ("KBSC Menu Item", "Keyboard Shortcuts"), ("ExportSettings", "My Settings > Export Settings"),
             ("ImportSettings", "My Settings > Import Settings"), ("preference", "Preferences > General"), ("selectionPref", "Preferences > Selection & Anchor Display"),
             ("keyboardPref", "Preferences > Type"), ("unitundoPref", "Preferences > Units"), ("guidegridPref", "Preferences > Guides & Grid"),
             ("snapPref", "Preferences > Smart Guides"), ("slicePref", "Preferences > Slices"), ("hyphenPref", "Preferences > Hyphenation"),
             ("pluginPref", "Preferences > Plug-ins & Scratch Disks"), ("userInterfacePref", "Preferences > User Interface"),
             ("GPUPerformancePref", "Preferences > Performance"), ("FilePref", "Preferences > File Handling"), ("ClipboardPref", "Preferences > Clipboard Handling"),
             ("BlackPref", "Preferences > Appearance of Black"), ("TouchPref", "Preferences > Touch Workspace"), ("DevicesPref", "Preferences > Devices")])
sec("Object", [("transformagain", "Transform > Transform Again"), ("transformmove", "Transform > Move"), ("transformrotate", "Transform > Rotate"),
               ("transformreflect", "Transform > Reflect"), ("transformscale", "Transform > Scale"), ("transformshear", "Transform > Shear"),
               ("Transform v23", "Transform > Transform Each"), ("AI Reset Bounding Box", "Transform > Reset Bounding Box"),
               ("sendToFront", "Arrange > Bring to Front"), ("sendForward", "Arrange > Bring Forward"), ("sendBackward", "Arrange > Send Backward"),
               ("sendToBack", "Arrange > Send to Back"), ("Selection Hat 2", "Arrange > Send to Current Layer"),
               ("Horizontal Align Left", "Align > Horizontal Align Left"), ("Horizontal Align Center", "Align > Horizontal Align Center"),
               ("Horizontal Align Right", "Align > Horizontal Align Right"), ("Vertical Align Top", "Align > Vertical Align Top"),
               ("Vertical Align Center", "Align > Vertical Align Center"), ("Vertical Align Bottom", "Align > Vertical Align Bottom"),
               ("Vertical Distribute Top", "Distribute > Vertical Distribute Top"), ("Vertical Distribute Center", "Distribute > Vertical Distribute Center"),
               ("Vertical Distribute Bottom", "Distribute > Vertical Distribute Bottom"), ("Horizontal Distribute Left", "Distribute > Horizontal Distribute Left"),
               ("Horizontal Distribute Center", "Distribute > Horizontal Distribute Center"), ("Horizontal Distribute Right", "Distribute > Horizontal Distribute Right"),
               ("group", "Group"), ("ungroup", "Ungroup"), ("lock", "Lock > Selection"), ("Selection Hat 5", "Lock > All Artwork Above"),
               ("Selection Hat 7", "Lock > Other Layers"), ("unlockAll", "Unlock All"), ("hide", "Hide > Selection"), ("Selection Hat 4", "Hide > All Artwork Above"),
               ("Selection Hat 6", "Hide > Other Layers"), ("showAll", "Show All"), ("Expand3", "Expand"), ("expandStyle", "Expand Appearance"),
               ("Crop Image", "Crop Image"), ("Rasterize 8 menu item", "Rasterize"), ("make mesh", "Create Gradient Mesh"),
               ("AI Object Mosaic Plug-in4", "Create Object Mosaic"), ("TrimMark v25", "Create Trim Marks"), ("Flatten Transparency", "Flatten Transparency"),
               ("Make Pixel Perfect", "Make Pixel Perfect"), ("AISlice Make Slice", "Slice > Make"), ("AISlice Release Slice", "Slice > Release"),
               ("AISlice Create from Guides", "Slice > Create from Guides"), ("AISlice Create from Selection", "Slice > Create from Selection"),
               ("AISlice Duplicate", "Slice > Duplicate Slice"), ("AISlice Combine", "Slice > Combine Slices"), ("AISlice Divide", "Slice > Divide Slices"),
               ("AISlice Delete All Slices", "Slice > Delete All"), ("AISlice Slice Options", "Slice > Slice Options"), ("AISlice Clip to Artboard", "Slice > Clip to Artboard"),
               ("join", "Path > Join"), ("average", "Path > Average"), ("OffsetPath v22", "Path > Outline Stroke"), ("OffsetPath v23", "Path > Offset Path"),
               ("Reverse Path Direction", "Path > Reverse Path Direction"), ("simplify menu item", "Path > Simplify"), ("smooth menu item", "Path > Smooth"),
               ("Add Anchor Points2", "Path > Add Anchor Points"), ("Remove Anchor Points menu", "Path > Remove Anchor Points"),
               ("Knife Tool2", "Path > Divide Objects Below"), ("Rows and Columns....", "Path > Split Into Grid"), ("cleanup menu item", "Path > Clean Up"),
               ("Convert to Shape", "Shape > Convert to Shapes"), ("Expand Shape", "Shape > Expand Shape"), ("Adobe Make Pattern", "Pattern > Make"),
               ("Adobe Edit Pattern", "Pattern > Edit Pattern"), ("Adobe Pattern Tile Color", "Pattern > Tile Edge Color"), ("Text To Pattern", "Pattern > Text to Pattern (Beta)"),
               ("Make Radial Repeat", "Repeat > Radial"), ("Make Grid Repeat", "Repeat > Grid"), ("Make Symmetry Repeat", "Repeat > Mirror"),
               ("Release Repeat Art", "Repeat > Release"), ("Repeat Art Options", "Repeat > Options"), ("Partial Rearrange Make", "Intertwine > Make"),
               ("Partial Rearrange Release", "Intertwine > Release"), ("Partial Rearrange Edit", "Intertwine > Edit"), ("Path Blend Make", "Blend > Make"),
               ("Path Blend Release", "Blend > Release"), ("Path Blend Options", "Blend > Blend Options"), ("Path Blend Expand", "Blend > Expand"),
               ("Path Blend Replace Spine", "Blend > Replace Spine"), ("Path Blend Reverse Spine", "Blend > Reverse Spine"),
               ("Path Blend Reverse Stack", "Blend > Reverse Front to Back"), ("Make Warp", "Envelope Distort > Make with Warp"),
               ("Create Envelope Grid", "Envelope Distort > Make with Mesh"), ("Make Envelope", "Envelope Distort > Make with Top Object"),
               ("Release Envelope", "Envelope Distort > Release"), ("Envelope Options", "Envelope Distort > Envelope Options"),
               ("Expand Envelope", "Envelope Distort > Expand"), ("Edit Envelope Contents", "Envelope Distort > Edit Contents"),
               ("Attach to Active Plane", "Perspective > Attach to Active Plane"), ("Release with Perspective", "Perspective > Release with Perspective"),
               ("Show Object Grid Plane", "Perspective > Move Plane to Match Object"), ("Edit Original Object", "Perspective > Edit Text"),
               ("Make Planet X", "Live Paint > Make"), ("Marge Planet X", "Live Paint > Merge"), ("Release Planet X", "Live Paint > Release"),
               ("Planet X Options", "Live Paint > Gap Options"), ("Expand Planet X", "Live Paint > Expand"), ("Make Vector Edge", "Mockup (Beta) > Make"),
               ("Release Vector Edge", "Mockup (Beta) > Release"), ("Edit Vector Edge", "Mockup (Beta) > Edit"), ("Make Image Tracing", "Image Trace > Make"),
               ("Make and Expand Image Tracing", "Image Trace > Make and Expand"), ("Release Image Tracing", "Image Trace > Release"),
               ("Expand Image Tracing", "Image Trace > Expand"), ("Make Text Wrap", "Text Wrap > Make"), ("Release Text Wrap", "Text Wrap > Release"),
               ("Text Wrap Options...", "Text Wrap > Text Wrap Options"), ("makeMask", "Clipping Mask > Make"), ("releaseMask", "Clipping Mask > Release"),
               ("editMask", "Clipping Mask > Edit Mask"), ("compoundPath", "Compound Path > Make"), ("noCompoundPath", "Compound Path > Release"),
               ("setCropMarks", "Artboards > Convert to Artboards"), ("ReArrange Artboards", "Artboards > Rearrange All Artboards"),
               ("Fit Artboard to artwork bounds", "Artboards > Fit to Artwork Bounds"), ("Fit Artboard to selected Art", "Artboards > Fit to Selected Art"),
               ("setGraphStyle", "Graph > Type"), ("editGraphData", "Graph > Data"), ("graphDesigns", "Graph > Design"), ("setBarDesign", "Graph > Column"),
               ("setIconDesign", "Graph > Marker"), ("collectForExportSingleAsset", "Collect For Export > As Single Asset"),
               ("collectForExportMultipleAsset", "Collect For Export > As Multiple Assets")])
sec("Type", [("Browse Typekit Fonts Menu IllustratorUI", "More from Adobe Fonts"), ("alternate glyph palette plugin", "Glyphs"),
             ("point-area", "Convert To Area Type / Point Type"), ("areatextoptions", "Area Type Options"),
             ("textpathtypeRainbow", "Type on a Path > Rainbow"), ("textpathtypeSkew", "Type on a Path > Skew"), ("textpathtype3d", "Type on a Path > 3D Ribbon"),
             ("textpathtypestairs", "Type on a Path > Stair Step"), ("textpathtypeGravity", "Type on a Path > Gravity"),
             ("textpathtypeOptions", "Type on a Path > Type on a Path Options"), ("updateLegacyTOP", "Type on a Path > Update Legacy Type on a Path"),
             ("Adobe internal composite font plugin", "Composite Fonts"), ("Adobe Kinsoku Settings", "Kinsoku Shori Settings"),
             ("Adobe MojiKumi Settings", "Mojikumi Settings"), ("threadTextCreate", "Threaded Text > Create"),
             ("releaseThreadedTextSelection", "Threaded Text > Release Selection"), ("removeThreading", "Threaded Text > Remove Threading"),
             ("fitHeadline", "Fit Headline"), ("Adobe IllustratorUI Resolve Missing Font", "Resolve Missing Fonts"),
             ("Adobe Illustrator Find Font Menu Item", "Find/Replace Font"), ("UpperCase Change Case Item", "Change Case > UPPERCASE"),
             ("LowerCase Change Case Item", "Change Case > lowercase"), ("Title Case Change Case Item", "Change Case > Title Case"),
             ("Sentence case Change Case Item", "Change Case > Sentence case"), ("Adobe Illustrator Smart Punctuation Menu Item", "Smart Punctuation"),
             ("outline", "Create Outlines"), ("Adobe Optical Alignment Item", "Optical Margin Alignment"),
             ("~bullet", "Insert Special Character > Symbols > Bullet"), ("~copyright", "Insert Special Character > Symbols > Copyright Symbol"),
             ("~ellipsis", "Insert Special Character > Symbols > Ellipsis"), ("~paragraphSymbol", "Insert Special Character > Symbols > Paragraph Symbol"),
             ("~registeredTrademark", "Insert Special Character > Symbols > Registered Trademark Symbol"),
             ("~sectionSymbol", "Insert Special Character > Symbols > Section Symbol"), ("~trademarkSymbol", "Insert Special Character > Symbols > Trademark Symbol"),
             ("~emDash", "Insert Special Character > Hyphens and Dashes > Em Dash"), ("~enDash", "Insert Special Character > Hyphens and Dashes > En Dash"),
             ("~discretionaryHyphen", "Insert Special Character > Hyphens and Dashes > Discretionary Hyphen"),
             ("~doubleLeftQuote", "Insert Special Character > Quotation Marks > Double Left Quotation Marks"),
             ("~doubleRightQuote", "Insert Special Character > Quotation Marks > Double Right Quotation Marks"),
             ("~singleLeftQuote", "Insert Special Character > Quotation Marks > Single Left Quotation Mark"),
             ("~singleRightQuote", "Insert Special Character > Quotation Marks > Single Right Quotation Mark"),
             ("~emSpace", "Insert Whitespace Character > Em Space"), ("~enSpace", "Insert Whitespace Character > En Space"),
             ("~hairSpace", "Insert Whitespace Character > Hair Space"), ("~thinSpace", "Insert Whitespace Character > Thin Space"),
             ("~forcedLineBreak", "Insert Break Character > Forced Line Break"), ("~placeHolderText", "Fill with Placeholder Text"),
             ("showHiddenChar", "Show Hidden Characters"), ("type-horizontal", "Type Orientation > Horizontal"), ("type-vertical", "Type Orientation > Vertical"),
             ("convertlegacyText", "Legacy Text > Update All Legacy Text"), ("convertlegacyText1", "Legacy Text > Update Selected Legacy Text"),
             ("convertlegacyText2", "Legacy Text > Hide Copies"), ("convertlegacyText3", "Legacy Text > Delete Copies"),
             ("convertlegacyText4", "Legacy Text > Select Copies")])
sec("Select", [("selectall", "All"), ("selectallinartboard", "All on Active Artboard"), ("deselectall", "Deselect"), ("Find Reselect menu item", "Reselect"),
               ("Inverse menu item", "Inverse"), ("Selection Hat 8", "Next Object Above"), ("Selection Hat 9", "Next Object Below"),
               ("Find Appearance menu item", "Same > Appearance"), ("Find Appearance Attributes menu item", "Same > Appearance Attribute"),
               ("Find Blending Mode menu item", "Same > Blending Mode"), ("Find Fill & Stroke menu item", "Same > Fill & Stroke"),
               ("Find Fill Color menu item", "Same > Fill Color"), ("Find Opacity menu item", "Same > Opacity"), ("Find Stroke Color menu item", "Same > Stroke Color"),
               ("Find Stroke Weight menu item", "Same > Stroke Weight"), ("Find Style menu item", "Same > Graphic Style"), ("Find Live Shape menu item", "Same > Shape"),
               ("Find Symbol Instance menu item", "Same > Symbol Instance"), ("Find Link Block Series menu item", "Same > Link Block Series"),
               ("Find Text Font Family menu item", "Same > Font Family"), ("Find Text Font Family Style menu item", "Same > Font Family & Style"),
               ("Find Text Font Family Style Size menu item", "Same > Font Family, Style & Size"), ("Find Text Font Size menu item", "Same > Font Size"),
               ("Find Text Fill Color menu item", "Same > Text Fill Color"), ("Find Text Stroke Color menu item", "Same > Text Stroke Color"),
               ("Find Text Fill Stroke Color menu item", "Same > Text Fill & Stroke Color"), ("Selection Hat 3", "Object > All on Same Layers"),
               ("Selection Hat 1", "Object > Direction Handles"), ("Bristle Brush Strokes menu item", "Object > Bristle Brush Strokes"),
               ("Brush Strokes menu item", "Object > Brush Strokes"), ("Clipping Masks menu item", "Object > Clipping Masks"),
               ("Stray Points menu item", "Object > Stray Points"), ("Text Objects menu item", "Object > All Text Objects"),
               ("Point Text Objects menu item", "Object > Point Text Objects"), ("Area Text Objects menu item", "Object > Area Text Objects"),
               ("SmartEdit Menu Item", "Start Global Edit"), ("Selection Hat 10", "Save Selection"), ("Selection Hat 11", "Edit Selection"),
               ("Selection Hat 14", "Update Selection")])
PSF = {"GEfc": "Effect Gallery", "ClrH": "Pixelate > Color Halftone", "Crst": "Pixelate > Crystallize", "Mztn": "Pixelate > Mezzotint",
       "Pntl": "Pixelate > Pointillize", "DfsG": "Distort > Diffuse Glow", "OcnR": "Distort > Ocean Ripple", "Gls ": "Distort > Glass",
       "RdlB": "Blur > Radial Blur", "SmrB": "Blur > Smart Blur", "Crsh": "Brush Strokes > Crosshatch", "SprS": "Brush Strokes > Sprayed Strokes",
       "Smie": "Brush Strokes > Sumi-e", "AccE": "Brush Strokes > Accented Edges", "InkO": "Brush Strokes > Ink Outlines", "Spt ": "Brush Strokes > Spatter",
       "AngS": "Brush Strokes > Angled Strokes", "DrkS": "Brush Strokes > Dark Strokes", "MscT": "Texture > Mosaic Tiles", "StnG": "Texture > Stained Glass",
       "Ptch": "Texture > Patchwork", "Grn ": "Texture > Grain", "Txtz": "Texture > Texturizer", "Crql": "Texture > Craquelure", "NtPr": "Sketch > Note Paper",
       "Stmp": "Sketch > Stamp", "Phtc": "Sketch > Photocopy", "WtrP": "Sketch > Water Paper", "Chrc": "Sketch > Charcoal", "GraP": "Sketch > Graphic Pen",
       "Plst": "Sketch > Plaster", "BsRl": "Sketch > Bas Relief", "ChlC": "Sketch > Chalk & Charcoal", "HlfS": "Sketch > Halftone Pattern",
       "Rtcl": "Sketch > Reticulation", "CntC": "Sketch > Conté Crayon", "TrnE": "Sketch > Torn Edges", "Chrm": "Sketch > Chrome", "DryB": "Artistic > Dry Brush",
       "PlsW": "Artistic > Plastic Wrap", "SmdS": "Artistic > Smudge Stick", "PntD": "Artistic > Paint Daubs", "Frsc": "Artistic > Fresco",
       "ClrP": "Artistic > Colored Pencil", "Ct  ": "Artistic > Cutout", "Wtrc": "Artistic > Watercolor", "PstE": "Artistic > Poster Edges",
       "Spng": "Artistic > Sponge", "FlmG": "Artistic > Film Grain", "RghP": "Artistic > Rough Pastels", "Undr": "Artistic > Underpainting",
       "PltK": "Artistic > Palette Knife", "NGlw": "Artistic > Neon Glow", "NTSC": "Video > NTSC Colors", "Dntr": "Video > De-Interlace",
       "GlwE": "Stylize > Glowing Edges"}
sec("Effect", [("Adobe Apply Last Effect", "Apply Last Effect"), ("Adobe Last Effect", "Last Effect"),
               ("Live Rasterize Effect Setting", "Document Raster Effects Settings"), ("Live Adobe Geometry3D Extrude", "3D and Materials > Extrude & Bevel"),
               ("Live Adobe Geometry3D Revolve", "3D and Materials > Revolve"), ("Live Adobe Geometry3D Inflate", "3D and Materials > Inflate"),
               ("Live Adobe Geometry3D Rotate", "3D and Materials > Rotate"), ("Live Adobe Geometry3D Materials", "3D and Materials > Materials"),
               ("Live 3DExtrude", "3D and Materials > 3D (Classic) > Extrude & Bevel (Classic)"), ("Live 3DRevolve", "3D and Materials > 3D (Classic) > Revolve (Classic)"),
               ("Live 3DRotate", "3D and Materials > 3D (Classic) > Rotate (Classic)"), ("Live SVG Filters", "SVG Filters > Apply SVG Filter"),
               ("SVG Filter Import", "SVG Filters > Import SVG Filter")]
    + [(f"Live Deform {w}", f"Warp > {w}") for w in ["Arc", "Arc Lower", "Arc Upper", "Arch", "Bulge", "Shell Lower", "Shell Upper", "Flag", "Wave", "Fish", "Rise", "Fisheye", "Inflate", "Squeeze", "Twist"]]
    + [("Live Roughen", "Distort & Transform > Roughen"), ("Live Pucker & Bloat", "Distort & Transform > Pucker & Bloat"), ("Live Twist", "Distort & Transform > Twist"),
       ("Live Transform", "Distort & Transform > Transform"), ("Live Zig Zag", "Distort & Transform > Zig Zag"), ("Live Free Distort", "Distort & Transform > Free Distort"),
       ("Live Scribble and Tweak", "Distort & Transform > Tweak"), ("Live Trim Marks", "Crop Marks"), ("Live Offset Path", "Path > Offset Path"),
       ("Live Outline Object", "Path > Outline Object"), ("Live Outline Stroke", "Path > Outline Stroke")]
    + [(f"Live Pathfinder {w}", f"Pathfinder > {n}") for w, n in [("Add", "Add"), ("Intersect", "Intersect"), ("Exclude", "Exclude"), ("Subtract", "Subtract"),
                                                                   ("Minus Back", "Minus Back"), ("Divide", "Divide"), ("Trim", "Trim"), ("Merge", "Merge"), ("Crop", "Crop"),
                                                                   ("Outline", "Outline"), ("Hard Mix", "Hard Mix"), ("Soft Mix", "Soft Mix"), ("Trap", "Trap")]]
    + [("Live Rectangle", "Convert to Shape > Rectangle"), ("Live Rounded Rectangle", "Convert to Shape > Rounded Rectangle"), ("Live Ellipse", "Convert to Shape > Ellipse"),
       ("Live Inner Glow", "Stylize > Inner Glow"), ("Live Adobe Round Corners", "Stylize > Round Corners"), ("Live Scribble Fill", "Stylize > Scribble"),
       ("Live Outer Glow", "Stylize > Outer Glow"), ("Live Feather", "Stylize > Feather"), ("Live Adobe Drop Shadow", "Stylize > Drop Shadow"),
       ("Live Rasterize", "Rasterize"), ("Live Adobe PSL Gaussian Blur", "Blur > Gaussian Blur")]
    + [(f"Live PSAdapter_plugin_{k}", v) for k, v in PSF.items()])
sec("View", [("preview", "Outline / Preview"), ("OpenGLCompositorPreview", "GPU Preview / Preview on CPU"), ("ink", "Overprint Preview"), ("raster", "Pixel Preview"),
             ("TrimView", "Trim View"), ("Adobe Presentation Mode", "Presentation Mode"), ("proof-document", "Proof Setup > Working CMYK"),
             ("proof-mac-rgb", "Proof Setup > Legacy Macintosh RGB"), ("proof-win-rgb", "Proof Setup > Internet Standard RGB (sRGB)"),
             ("proof-monitor-rgb", "Proof Setup > Monitor RGB"), ("proof-colorblindp", "Proof Setup > Color blindness - Protanopia-type"),
             ("proof-colorblindd", "Proof Setup > Color blindness - Deuteranopia-type"), ("proof-custom", "Proof Setup > Customize"), ("proofColors", "Proof Colors"),
             ("zoomin", "Zoom In"), ("zoomout", "Zoom Out"), ("fitin", "Fit Artboard in Window"), ("fitall", "Fit All in Window")]
    + [(f"RotateView{a}", f"Rotate View > {a}°") for a in ["180", "150", "135", "120", "90", "60", "45", "30", "15"]] + [("RotateViewZero", "Rotate View > 0°")]
    + [(f"RotateViewNegative{a}", f"Rotate View > -{a}°") for a in ["15", "30", "45", "60", "90", "120", "135", "150", "180"]]
    + [("resetRotationView", "Reset Rotate View"), ("rotateViewToSelection", "Rotate View to Selection"), ("AISlice Feedback Menu", "Hide Slices"),
       ("AISlice Lock Menu", "Lock Slices"), ("AI Bounding Box Toggle", "Hide Bounding Box"), ("TransparencyGrid Menu Item", "Show Transparency Grid"),
       ("actualsize", "Actual Size"), ("Gradient Feedback", "Hide Gradient Annotator"), ("Show Gaps Planet X", "Show Live Paint Gaps"),
       ("Live Corner Annotator", "Hide Corner Widget"), ("edge", "Hide Edges"), ("Snapomatic on-off menu item", "Smart Guides"),
       ("Show Perspective Grid", "Perspective Grid > Show Grid"), ("Show Ruler", "Perspective Grid > Show Rulers"), ("Snap to Grid", "Perspective Grid > Snap to Grid"),
       ("Lock Perspective Grid", "Perspective Grid > Lock Grid"), ("Lock Station Point", "Perspective Grid > Lock Station Point"),
       ("Define Perspective Grid", "Perspective Grid > Define Grid"), ("Save Perspective Grid as Preset", "Perspective Grid > Save Grid as Preset"),
       ("artboard", "Hide Artboards"), ("pagetiling", "Show Print Tiling"), ("showtemplate", "Show Template"), ("ruler", "Rulers > Show Rulers"),
       ("rulerCoordinateSystem", "Rulers > Change to Global Rulers"), ("videoruler", "Rulers > Show Video Rulers"), ("textthreads", "Show Text Threads"),
       ("showguide", "Guides > Hide Guides"), ("lockguide", "Guides > Lock Guides"), ("makeguide", "Guides > Make Guides"), ("releaseguide", "Guides > Release Guides"),
       ("clearguide", "Guides > Clear Guides"), ("showgrid", "Show Grid"), ("snapgrid", "Snap to Grid"), ("pixelconstraints", "Snap to Pixel"),
       ("snappoint", "Snap to Point"), ("glyphSnapping", "Snap to Glyph"), ("newview", "New View"), ("editview", "Edit Views")]
    + [(f"view{i}", f"Saved View {i}") for i in range(1, 11)])
sec("Window", [("newwindow", "New Window"), ("cascade", "Arrange > Cascade"), ("tile", "Arrange > Tile"), ("floatInWindow", "Arrange > Float in Window"),
               ("floatAllInWindows", "Arrange > Float All in Windows"), ("consolidateAllWindows", "Arrange > Consolidate All Windows"),
               ("Browse Add-Ons Menu", "Find Extensions on Exchange"), ("Adobe Touch Workspace", "Workspace > Touch"), ("Adobe Reset Workspace", "Workspace > Reset"),
               ("Adobe New Workspace", "Workspace > New Workspace"), ("Adobe Manage Workspace", "Workspace > Manage Workspaces"),
               ("Adobe Basic Toolbar Menu", "Toolbars > Basic"), ("Adobe Advanced Toolbar Menu", "Toolbars > Advanced"), ("New Tools Panel", "Toolbars > New Toolbar"),
               ("Manage Tools Panel", "Toolbars > Manage Toolbar"), ("drover control palette plugin", "Control"), ("Adobe 3D Panel", "3D and Materials"),
               ("CSS Menu Item", "CSS Properties"), ("ReTypeWindowMenu", "Retype (Beta)"), ("Adobe SVG Interactivity Palette", "SVG Interactivity"),
               ("Generate", "Generate Patterns (Beta)"), ("Adobe Property Palette", "Properties"), ("Adobe Separation Preview Panel", "Separations Preview"),
               ("Adobe Action Palette", "Actions"), ("AdobeLayerPalette1", "Layers"), ("Adobe Pattern Panel Toggle", "Pattern Options"), ("Style Palette", "Asset Export"),
               ("AdobeAlignObjects2", "Align"), ("AdobeNavigator", "Navigator"), ("internal palettes posing as plug-in menus-attributes", "Attributes"),
               ("Adobe Artboard Palette", "Artboards"), ("Adobe Flattening Preview", "Flattener Preview"), ("Adobe Vectorize Panel", "Image Trace"),
               ("DocInfo1", "Document Info"), ("internal palettes posing as plug-in menus-opentype", "Type > OpenType"),
               ("internal palettes posing as plug-in menus-character", "Type > Character"), ("Character Styles", "Type > Character Styles"),
               ("alternate glyph palette plugin 2", "Type > Glyphs"), ("internal palettes posing as plug-in menus-tab", "Type > Tabs"),
               ("internal palettes posing as plug-in menus-paragraph", "Type > Paragraph"), ("Adobe Paragraph Styles Palette", "Type > Paragraph Styles"),
               ("Adobe Vector Edge Panel", "Mockup (Beta)"), ("Adobe History Panel Menu Item", "History"), ("Adobe Gradient Palette", "Gradient"),
               ("Adobe Symbol Palette", "Symbols"), ("Adobe BrushManager Menu Item", "Brushes"), ("Adobe Stroke Palette", "Stroke"), ("Adobe Style Palette", "Graphic Styles"),
               ("Adobe Harmony Palette", "Color Guide"), ("Adobe Swatches Menu Item", "Swatches"), ("AdobeTransformObjects1", "Transform"),
               ("Adobe Variables Palette Menu Item", "Variables"), ("Adobe CSXS Extension com.adobe.DesignLibraries.angular\\750\\663\\607\\746\\626\\631\\745\\672\\653", "Libraries"),
               ("Adobe SmartExport Panel Menu Item", "Asset Export"), ("internal palettes posing as plug-in menus-info", "Info"), ("Adobe PathfinderUI", "Pathfinder"),
               ("Adobe Transparency Palette Menu Item", "Transparency"), ("Adobe LinkPalette Menu Item", "Links"), ("Adobe Color Palette", "Color"),
               ("AI Magic Wand", "Magic Wand"), ("Adobe Symbol Palette Plugin Other libraries menu item", "Symbol Libraries > Other Library"),
               ("AdobeBrushMgrUI Other libraries menu item", "Brush Libraries > Other Library"), ("Adobe Art Style Plugin Other libraries menu item", "Graphic Style Libraries > Other Library"),
               ("AdobeSwatch_ Other libraries menu item", "Swatch Libraries > Other Library")])
sec("Help", [("helpcontent", "Illustrator Help"), ("supportContent", "Support Center"), ("whatsNewContent", "What's New"), ("supportCommunity", "Community"),
             ("wishform", "Submit Bug/Feature Request"), ("systemInfo", "System Info"), ("about", "About Illustrator")])
KB = {"switchSelTool": "Switch Selection Tools", "faceSizeUp": "Font Size Up (large step)", "faceSizeDown": "Font Size Down (large step)", "sizeStepUp": "Font Size Up",
      "sizeStepDown": "Font Size Down", "~kernFurther": "Kern/Track Looser", "~kernCloser": "Kern/Track Tighter", "tracking": "Tracking Looser (word)",
      "clearTrack": "Clear Tracking", "spacing": "Word Spacing", "clearTypeScale": "Reset Horizontal/Vertical Scale", "highlightFont": "Highlight Font", "highlightFont2": "Highlight Font (alt)",
      "leftAlign": "Align Text Left", "centerAlign": "Align Text Center", "rightAlign": "Align Text Right", "justify": "Justify Left", "justifyCenter": "Justify Center",
      "justifyRight": "Justify Right", "justifyAll": "Justify All Lines", "toggleAutoHyphen": "Toggle Auto Hyphenation", "toggleLineComposer": "Toggle Line Composer",
      "~subscript": "Subscript", "~superScript": "Superscript", "lock2": "Lock Unselected Artwork", "hide2": "Hide Unselected Artwork", "repeatPathfinder": "Repeat Pathfinder",
      "avgAndJoin": "Average and Join", "enterFocus": "Enter Isolation Mode", "exitFocus": "Exit Isolation Mode", "Adobe New Symbol Shortcut": "New Symbol",
      "Adobe Color Palette Secondary": "Cycle Color Modes", "Adobe Actions Batch": "Actions Batch", "Adobe New Fill Shortcut": "Add New Fill",
      "Adobe New Stroke Shortcut": "Add New Stroke", "Adobe New Style Shortcut": "New Graphic Style", "AdobeLayerPalette2": "New Layer",
      "AdobeLayerPalette3": "New Layer with Options", "Adobe Update Link Shortcut": "Update Link", "Adobe New Swatch Shortcut Menu": "New Swatch", "Debug Panel": "Debug Panel",
      "switchUnits": "Cycle Units", "new2": "New (alternate)", "closeAll2": "Close All (alternate)", "helpcontent2": "Help (alternate)", "undo2": "Undo (alternate)",
      "cut2": "Cut (alternate)", "copy2": "Copy (alternate)", "paste2": "Paste (alternate)", "zoomin2": "Zoom In (alternate)", "debugPalette": "Debug Palette",
      "navigateToNextDocument": "Next Document", "navigateToPreviousDocument": "Previous Document", "navigateToNextDocumentGroup": "Next Document Group",
      "navigateToPreviousDocumentGroup": "Previous Document Group", "~subscript2": "Subscript (alternate)", "~superScript2": "Superscript (alternate)"}
sec("Keyboard", list(KB.items()))


def main():
    kys = sorted(RAW.glob("ai*_commands.kys"))[-1]
    data, keys = parse_kys(kys)
    menus = data["Menus"][::-1]                   # the .kys lists menu commands bottom-up
    tools = data["Tools"][::-1]
    missing = [c for c in menus if c not in P]
    if missing:
        print("commands without a path (add them to the table):", missing)
    items = []
    for c in menus:
        path = P.get(c, f"Other > {c}")
        k = keys.get(("Menus", c), {})
        items.append({"cmd": c, "path": path, "top": path.split(" > ")[0], "key": k.get("Key", 0), "mods": k.get("Modifiers", 0)})
    tl = [{"tool": t} for t in tools]
    out = {"source": kys.name, "items": items, "tools": tl}
    (HERE / "menu-index.json").write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding="utf-8")
    tops = {}
    for it in items:
        tops[it["top"]] = tops.get(it["top"], 0) + 1
    print(f"{len(items)} menu commands, {len(tl)} tools; per menu: {tops}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

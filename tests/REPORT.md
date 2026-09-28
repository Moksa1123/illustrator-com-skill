# ailib test report

- Illustrator 28.0.0 | 2026-09-28T08:21:13 | **40/40 pass**

| Area | Function | Result | Read back |
|---|---|---|---|
| shapes | rect at artboard top-left coords | ✅ | AI.box = 100,50,200,120 / 3 pixels sampled |
| shapes | roundRect / ellipse / circle / polygon / star | ✅ | rounded corners 8 pts, hexagon 6, star 10, circle 100x100 at 450,20 / 4 pixels sampled |
| shapes | line with stroke style (dash, cap) | ✅ | 8 pt dashed [20,10], round caps / 1 pixels sampled |
| shapes | bezier path + SVG path data | ✅ | bezier handles set; SVG "M…Z M…Z" -> compound path with a hole / 2 pixels sampled |
| color | hex / CMYK / gray / spot / swatch | ✅ | hex #1e90ff -> 30,144,255; gray 50%; spot "Brand Red" tint 60; swatch "brand blue" |
| color | linear + radial gradient fills | ✅ | linear 2 stops (red→blue), radial 3 stops with midpoint 30 / 3 pixels sampled |
| style | opacity / blend mode / layer / name | ✅ | 50% multiply on layer "FX" / 1 pixels sampled |
| layout | moveTo / scaleTo (keep aspect) / rotate / flip | ✅ | move to 300,200; fit 200x200 keep aspect -> 200x100; rotate 90 swaps w/h; flip mirrors anchors |
| layout | align to artboard and to selection | ✅ | centered on 800 pt artboard (x 350 / 375); bottoms equal; key-object top align |
| layout | distribute equal spacing / fixed gap / grid | ✅ | equal gaps 190 pt; fixed 10 pt gap; 3-column grid |
| structure | group / ungroup | ✅ | group of 2 named "pair", ungroup restores 2 items |
| structure | clipping mask | ✅ | circle clips the square / 2 pixels sampled |
| structure | compound path (hole) | ✅ | outer 300x300, inner 100x100 hole / 2 pixels sampled |
| pathfinder | unite / minusFront / intersect / exclude | ✅ | unite 150x150, minus front keeps the back 70 wide, intersect 50x50, exclude hole / 2 pixels sampled |
| pathfinder | divide / trim / crop | ✅ | divide -> 3 pieces; crop keeps the circle area |
| text | point text: font, size, color, tracking, top-left placement | ✅ | Arial 48 pt, tracking 50, top of text box at y 100 (100,100,360.9,56.8) |
| text | area text: width, alignment, leading | ✅ | area text 300 wide wraps to 3 lines, centered, leading 30 |
| text | mixed styles in one frame (runs) | ✅ | "Big " 60 pt red + "small" 20 pt blue underlined |
| text | vertical CJK text + OpenType caps | ✅ | vertical frame 585,50,30,180; SMALLCAPS + fractions |
| text | text on a path | ✅ | PATHTEXT on a circle |
| text | fit text to width + create outlines | ✅ | shrunk to ≤300 wide, then outlined -> group of paths |
| text | character + paragraph styles | ✅ | character style "Accent" 40 pt red; paragraph style "Body" right, space after 12 |
| effects | drop shadow + outer glow + round corners | ✅ | shadow widens visible bounds by 19 pt / effects read back: Adobe Drop Shadow, Adobe Round Corners, Adobe Outer Glow |
| effects | offset path / feather / gaussian blur / roughen / warp | ✅ | offset path grows visible bounds by 15 pt; 5 effects stored / effects read back: Adobe Offset Path, Adobe Fuzzy Mask, Adobe PSL Gaussian Blur, Adobe Roughen, Adobe Deform |
| effects | expand appearance | ✅ | offset baked into geometry: 140 pt wide |
| image | place + embed + fit + clip image | ✅ | placed 200 wide (linked), embedded RasterItem 150 wide, clipped to circle |
| image | image trace -> vector paths | ✅ | traced raster -> 2 paths |
| image | rasterize vector art | ✅ | star -> RasterItem / 1 pixels sampled |
| symbols | symbol create + place instances | ✅ | symbol "StarSym" with 2 instances |
| symbols | graphic style applied | ✅ | applied "製作陰影" (7 styles available) |
| structure | repeat radial / grid / mirror | ✅ | RadialRepeatItem, GridRepeatItem, SymmetryRepeatItem |
| structure | blend two shapes | ✅ | blend object (PluginItem) |
| document | newDoc with safe-zone guides + background | ✅ | 1080×1920, guides H1248 H269 V1015 V65, locked background |
| document | multiple artboards + add + fit to art | ✅ | 3 artboards + "extra"; fit artboard to selected art = 50x60 |
| document | layers: create, lock, hide, order | ✅ | layer "Top" in front, "Hidden" invisible |
| export | PNG / JPG / WebP / SVG / PDF / PSD | ✅ | png 50% / 200% transparent, jpg, webp, svg (outlined text), psd / 6 files decoded |
| export | export for screens (all artboards x 2 formats) | ✅ | 4 files (2 artboards × png@2x + svg) / 4 files decoded |
| export | PDF save + reopen | ✅ | PDF [High Quality Print]: 2 pages in the file, reopens in Illustrator / 1 files decoded |
| text | fit headline (tracking fills one line) | ✅ | tracking 1150 keeps "HEADLINE" on one 400 pt line |
| text | thread two area-text frames | ✅ | text flows from frame 1 into frame 2 (3 lines there) |

Only ✅ functions are for production use. Snapshots of every test document: tests/snaps/.

"""Example: a 1080x1350 social post built only with ailib (no dialogs), exported as PNG + SVG + AI.
Usage: python examples/make_post.py [out_dir]
"""
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL / "lib"))
from ai_run import run_js  # noqa: E402
from ailib_loader import library  # noqa: E402

out = Path(sys.argv[1] if len(sys.argv) > 1 else SKILL / "examples" / "out").resolve()
out.mkdir(parents=True, exist_ok=True)
O = out.as_posix()
print(run_js(library() + f"""
var D = AI.newDoc(1080, 1350, 'post', {{bg: '#f4efe8', safe: [0, 45, 0, 45]}});
var band = AI.rect(0, 0, 1080, 220, {{fill: AI.gradient([[0, '#c8a97e'], [1, '#8c6f52']], {{angle: 0}}), stroke: null}});
AI.text('STUDIO ROAST', 80, 90, {{font: 'Arial-BoldMT', size: 44, color: '#2b2520', tracking: 300}});
var title = AI.text('Bean & Heart', 80, 300, {{font: 'Georgia-Italic', size: 130, color: '#2b2520'}});
AI.fitText(title, 920);
var sub = AI.text('手沖咖啡 · 單品豆 · 每週新鮮烘焙', 80, 470, {{font: 'MicrosoftJhengHeiRegular', size: 44, color: '#8c6f52'}});
var card = AI.roundRect(80, 580, 920, 560, 36, {{fill: '#2b2520', stroke: null}});
AI.dropShadow(card, {{y: 12, blur: 16, opacity: 0.35}});
for (var i = 0; i < 3; i++) {{
  var cup = AI.circle(250 + i * 290, 800, 95, {{fill: ['#c8a97e', '#e6d3b3', '#8c6f52'][i], stroke: null}});
  AI.text(['淺焙', '中焙', '深焙'][i], 200 + i * 290, 930, {{font: 'MicrosoftJhengHeiBold', size: 40, color: '#f4efe8'}});
}}
var badge = AI.pathfinder([AI.circle(930, 1230, 80), AI.star(930, 1230, 55, 24, 5)], 'minusFront');
AI.style(badge, {{fill: '#8c6f52', stroke: null}});
var btn = AI.roundRect(80, 1190, 380, 90, 45, {{fill: '#2b2520', stroke: null}});
var bt = AI.text('SHOP NOW', 0, 0, {{font: 'Arial-BoldMT', size: 36, color: '#f4efe8', tracking: 120}});
AI.align([bt], 'hcenter', btn); AI.align([bt], 'vcenter', btn);
AI.png('{O}/post.png'); AI.svg('{O}/post.svg', {{outlineText: true}}); AI.saveAI('{O}/post.ai');
D.close(SaveOptions.DONOTSAVECHANGES);
'saved {O}/post.png, post.svg, post.ai'
"""))

"""Regression check for tools/html2ai.py: reads the converted document back from Illustrator.

    python tests/html2ai_check.py

1. "<span>for</span> WooCommerce": the second text frame starts after the first one plus a space (a leading space must
   not set the line's x, which glued the words together).
2. A box with a 5 % fill and a 12 % border: the border is its own stroke-only shape at 12 % opacity (it used to inherit
   the fill's 5 % and vanish).
3. linear-gradient(90deg, rgba(...,1), rgba(...,0)): the gradient's stops keep 100 % and 0 % opacity.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL / "lib"))
from ai_run import run_js  # noqa: E402

HTML = """<!doctype html><html><head><meta charset="utf-8"><style>
*{margin:0;padding:0} body{width:600px;height:300px;font-family:Arial,sans-serif}
.canvas{position:relative;width:600px;height:300px;background:#101828}
.t{position:absolute;left:20px;top:20px;font-size:40px;color:#fff;line-height:48px}
.card{position:absolute;left:20px;top:100px;width:200px;height:80px;border-radius:12px;border:1px solid rgba(255,255,255,0.12);background:rgba(255,255,255,0.05)}
.rule{position:absolute;left:20px;top:220px;width:400px;height:4px;background:linear-gradient(90deg,rgba(251,146,60,1),rgba(251,146,60,0))}
</style></head><body><div class="canvas"><div class="t"><span style="color:#fb923c">for</span> WooCommerce</div>
<div class="card"></div><div class="rule"></div></div></body></html>"""


def main():
    d = Path(tempfile.mkdtemp())
    (d / "t.html").write_text(HTML, encoding="utf-8")
    r = subprocess.run([sys.executable, str(SKILL / "tools/html2ai.py"), str(d / "t.html"), str(d / "t.ai"), "--w", "600", "--h", "300",
                        "--keep-open"], capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr[-800:]
    got = json.loads(run_js(r"""
var D = app.activeDocument, out = {texts: [], borders: [], grads: []};
for (var i = 0; i < D.textFrames.length; i++) { var t = D.textFrames[i], b = t.geometricBounds; out.texts.push({s: t.contents, l: b[0], r: b[2]}); }
for (var i = 0; i < D.pathItems.length; i++) { var p = D.pathItems[i];
  if (p.stroked && !p.filled) out.borders.push({op: p.opacity, n: p.name});
  if (p.filled && p.fillColor.typename == 'GradientColor') { var g = p.fillColor.gradient, st = [];
    for (var k = 0; k < g.gradientStops.length; k++) st.push(g.gradientStops[k].opacity); out.grads.push(st); } }
D.close(SaveOptions.DONOTSAVECHANGES);
var s = '{"texts":['; for (var i = 0; i < out.texts.length; i++) s += (i ? ',' : '') + '{"s":"' + out.texts[i].s + '","l":' + out.texts[i].l + ',"r":' + out.texts[i].r + '}';
s += '],"borders":['; for (var i = 0; i < out.borders.length; i++) s += (i ? ',' : '') + out.borders[i].op;
s += '],"grads":['; for (var i = 0; i < out.grads.length; i++) s += (i ? ',' : '') + '[' + out.grads[i].join(',') + ']';
s + ']}'
"""))
    texts = {t["s"]: t for t in got["texts"]}
    a, b = texts["for"], texts["WooCommerce"]
    gap = b["l"] - a["r"]
    ok1 = 6 <= gap <= 16                                       # one 40 px Arial space is about 11 pt
    ok2 = any(abs(o - 12) < 0.6 for o in got["borders"])
    ok3 = any(abs(g[0] - 100) < 0.6 and abs(g[-1]) < 0.6 for g in got["grads"])
    for name, ok, detail in (("space before a word keeps its x", ok1, f"gap {gap:.1f} pt"),
                             ("translucent border keeps its own alpha", ok2, f"stroke-only opacities {got['borders']}"),
                             ("gradient stops keep alpha", ok3, f"stop opacities {got['grads']}")):
        print(("PASS " if ok else "FAIL ") + name + " — " + detail)
    sys.exit(0 if ok1 and ok2 and ok3 else 1)


if __name__ == "__main__":
    main()

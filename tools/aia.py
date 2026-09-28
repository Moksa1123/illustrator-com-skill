"""Illustrator action files (.aia) from Python: play commands through the Actions engine.

Why: a few AI 2024 commands only act through an on-canvas widget while Illustrator is the active window
(Object > Path > Simplify / Smooth), and action events carry parameters that no dialog-free API exposes.
An action event is written in Illustrator's own .aia text layout, loaded with app.loadAction(), played with
app.doScript() and unloaded again, so nothing stays in the user's Actions panel.

    from aia import play_js, SIMPLIFY
    run_js(play_js([SIMPLIFY(precision=60)]))       # on the current selection

Event recipes come from Illustrator's shipped default action set (Presets/<locale>/Actions/*.aia) and from
recordings; parameter keys are 4-char codes as integers.
CLI: python tools/aia.py simplify [precision]
"""
import json
import sys


def _hex_block(s, indent):
    b = s.encode("utf-8")
    h = b.hex()
    lines = [h[i:i + 64] for i in range(0, len(h), 64)] or [""]
    pad = "\t" * (indent + 1)
    return f"[ {len(b)}\n" + "".join(f"{pad}{ln}\n" for ln in lines) + "\t" * indent + "]"


def event(internal, label, params, dialog=False):
    """params: list of dicts {key, type: 'unit real'|'real'|'integer'|'boolean'|'enumerated'|'ustring', value, unit?, name?}"""
    out = ["\t/event-{n} {", "\t\t/useRulersIn1stQuadrant 1", f"\t\t/internalName ({internal})", f"\t\t/localizedName {_hex_block(label, 2)}",
           "\t\t/isOpen 0", "\t\t/isOn 1", f"\t\t/hasDialog {1 if dialog else 0}"]
    if dialog:
        out.append("\t\t/showDialog 0")
    out.append(f"\t\t/parameterCount {len(params)}")
    for i, p in enumerate(params, 1):
        out += [f"\t\t/parameter-{i} {{", f"\t\t\t/key {p['key']}", "\t\t\t/showInPalette 1", f"\t\t\t/type ({p['type']})"]
        if p["type"] == "enumerated":
            out.append(f"\t\t\t/name {_hex_block(p.get('name', ''), 3)}")
        if p["type"] == "ustring":
            out.append(f"\t\t\t/value {_hex_block(p['value'], 3)}")
        else:
            v = p["value"]
            out.append(f"\t\t\t/value {int(v) if p['type'] in ('boolean', 'integer', 'enumerated') else float(v)}")
        if "unit" in p:
            out.append(f"\t\t\t/unit {p['unit']}")
        out.append("\t\t}")
    out.append("\t}")
    return "\n".join(out)


def action_set(set_name, actions):
    """actions: {action name: [event text, ...]} -> .aia text"""
    out = ["/version 3", f"/name {_hex_block(set_name, 0)}", "/isOpen 1", f"/actionCount {len(actions)}"]
    for ai, (aname, evs) in enumerate(actions.items(), 1):
        out += [f"/action-{ai} {{", f"\t/name {_hex_block(aname, 1)}", "\t/keyIndex 0", "\t/colorIndex 0", "\t/isOpen 1", f"\t/eventCount {len(evs)}"]
        for ei, ev in enumerate(evs, 1):
            out.append(ev.replace("{n}", str(ei)))
        out.append("}")
    return "\n".join(out) + "\n"


def play_js(events, set_name="ai_skill_tmp"):
    """ExtendScript that writes the events as one action, loads, plays and unloads it."""
    text = action_set(set_name, {"run": events})
    return ("(function () { var f = new File(Folder.temp + '/" + set_name + ".aia'); f.encoding = 'UTF-8'; f.lineFeed = 'Windows'; f.open('w'); f.write("
            + json.dumps(text) + "); f.close();"
            " try { app.unloadAction(" + json.dumps(set_name) + ", ''); } catch (e) {}"
            " app.loadAction(f); var err = '';"
            " try { app.doScript('run', " + json.dumps(set_name) + ", false); } catch (e) { err = String(e); }"
            " try { app.unloadAction(" + json.dumps(set_name) + ", ''); } catch (e) {} f.remove(); if (err) throw new Error(err); return 'played'; })()")


def c4(s):
    return int.from_bytes(s.encode("latin-1"), "big")


def SIMPLIFY(precision=40.0, angle=0.0, straight=False, show_original=False):
    """Object > Path > Simplify (curve precision %, angle threshold deg); recipe from Illustrator's default actions."""
    return event("ai_plugin_simplify", "Simplify", [
        {"key": 1919182693, "type": "unit real", "value": precision, "unit": 592474723},
        {"key": 1634561652, "type": "unit real", "value": angle, "unit": 591490663},
        {"key": 1936553064, "type": "boolean", "value": straight},
        {"key": 1936552044, "type": "boolean", "value": show_original}], dialog=True)


def PATHFINDER(op=0):
    """Pathfinder panel operation (enumerated: 0 = unite/add, ...) — recipe from Illustrator's default actions."""
    return event("ai_plugin_pathfinder", "Pathfinder", [{"key": 1851878757, "type": "enumerated", "name": "", "value": op}])


if __name__ == "__main__":
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent / "lib"))
    from ai_run import run_js
    if sys.argv[1] == "simplify":
        print(run_js(play_js([SIMPLIFY(float(sys.argv[2]) if len(sys.argv) > 2 else 40.0)]), dialog="esc"))

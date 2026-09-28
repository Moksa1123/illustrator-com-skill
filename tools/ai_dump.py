"""Read back what the DOM cannot: parse an *uncompressed* .ai file (IllustratorSaveOptions.compressed = false,
pdfCompatible = false) into Illustrator's own text-form document data.

  art_text(path)   the reassembled private data (PDF stream chunks joined), volatile parts removed
  art_hash(path)   stable hash of the artwork + document data (same art → same hash across saves)
  effects(path)    every live effect in the file: [{"name": "Adobe Offset Path", "params": {"ofst": 20, ...}}]
  sections(path)   rough split: palette (swatches), styles, layers

CLI:  python tools/ai_dump.py effects file.ai | hash file.ai | text file.ai | grep file.ai <regex>
"""
import hashlib
import json
import re
import sys
from pathlib import Path

_CHUNK = re.compile(rb"\r?\nendstream\s*endobj\s*\d+ 0 obj\s*<<\s*/Length \d+\s*>>\s*stream\r?\n")


def _raw(path):
    b = Path(path).read_bytes()
    i = b.find(b"%AI12_CompressedData")
    if i >= 0:
        raise ValueError("compressed .ai: save with IllustratorSaveOptions.compressed = false")
    s = b.find(b"%!PS-Adobe")
    if s < 0:
        raise ValueError("no Illustrator private data (was it saved with pdfCompatible only?)")
    body = _CHUNK.sub(b"", b[s:])
    e = body.find(b"%%EOF")
    return body[:e if e > 0 else len(body)]


VOLATILE = [
    re.compile(rb"^%%(Title|CreationDate|Creator|For|AI8_CreatorVersion|BoundingBox|HiResBoundingBox).*$", re.M),
    re.compile(rb"^%AI\d*_(Thumbnail|BeginThumbnail).*?^%AI\d*_EndThumbnail\s*$", re.M | re.S),
    re.compile(rb"^%%BeginData.*?^%%EndData\s*$", re.M | re.S),
    re.compile(rb"\(Anon [^)]*\)"),                    # anonymous style ids
    re.compile(rb"xmp\.(iid|did):[0-9a-f-]+|uuid:[0-9a-f-]+", re.I),
    re.compile(rb"\(\d{4}-\d\d-\d\dT[^)]*\)"),
    re.compile(rb"/Uuid\s*\([^)]*\)|\([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\)", re.I),
    re.compile(rb"^%AI\d+_Cropmarks.*$", re.M),
    # text engine blobs change on every save (session records); text is fingerprinted through the DOM instead
    re.compile(rb"/AI11\w*TextDocument : /ASCII85Decode ,\r?\n(?:%[^\n]*\n)+"),
]


def art_text(path):
    t = _raw(path)
    for rx in VOLATILE:
        t = rx.sub(b"", t)
    return t.decode("latin-1")


def art_hash(path):
    return hashlib.sha1(art_text(path).encode("latin-1")).hexdigest()[:16]


_NUM = re.compile(r"^-?\d+(\.\d+)?$")


def effects(path):
    """Live effects: '(Adobe Offset Path) 1 0 /Filter , ... /Dictionary : ... 4 /Real (mlim) , ... ; /Dict ;'"""
    t = art_text(path)
    out = []
    for m in re.finditer(r"/BasicFilter :\s*\n?\((.*?)\) (\d+) (\d+) /Filter ,(.*?)(?=/BasicFilter :|/Execution ;|\Z)", t, re.S):
        name, body = m.group(1), m.group(4)
        if name in ("Fill Style Filter", "Stroke Style Filter", "Blend Style Filter"):
            continue
        params, types = {}, {}
        dm = re.search(r"/Dictionary : /NotRecorded ,(.*?); /Dict ;", body, re.S)
        for pm in re.finditer(r"(\([^)]*\)|\S+) /(Real|Int|Bool|String|UnicodeString) \(([^)]*)\) ,", dm.group(1) if dm else ""):
            v, typ, key = pm.groups()
            if typ in ("Real", "Int") and _NUM.match(v):
                v = float(v) if typ == "Real" else int(v)
            elif typ == "Bool":
                v = v == "1"
            elif v.startswith("("):
                v = v[1:-1]
            params[key] = v
            types[key] = typ
        bm = re.search(r"/Binary : /ASCII85Decode ,\r?\n((?:%[^\n]*\n)+); \(data\) ,", dm.group(1) if dm else "")
        if bm:
            import base64
            raw = "".join(l.strip()[1:] for l in bm.group(1).splitlines()).strip()
            try:
                params["ps"] = ps_descriptor(base64.a85decode(raw[:-2] if raw.endswith("~>") else raw))
            except Exception as ex:  # noqa: BLE001
                params["ps"] = {"_error": str(ex)}
            types["ps"] = "PSDescriptor"
        vis = re.search(r"(\d) /Visible", body)
        out.append({"name": name, "visible": vis.group(1) == "1" if vis else None, "params": params, "types": types,
                    "nested": bool(dm and re.search(r"/(Dict|FillStyle|StrokeStyle|Art|Array) ", dm.group(1)))})
    return out


def ps_descriptor(b):
    """Photoshop-filter effects keep their parameters as a binary descriptor: version(4), then items of
    key(4) flags(4) type(4) value. long = int32, doub = float64, bool = 1 byte, UntF = unit(4) + float64;
    any other type is an enumeration whose value is a 4-char id (Filter Gallery: GEfk = GEft 'Crsh')."""
    import struct
    out, i = {}, 4
    while i + 12 <= len(b):
        key = b[i:i + 4].decode("latin-1")
        typ = b[i + 8:i + 12].decode("latin-1")
        i += 12
        if typ == "long":
            out[key] = struct.unpack(">i", b[i:i + 4])[0]; i += 4
        elif typ == "doub":
            out[key] = struct.unpack(">d", b[i:i + 8])[0]; i += 8
        elif typ == "bool":
            out[key] = bool(b[i]); i += 1
        elif typ == "UntF":
            out[key] = struct.unpack(">d", b[i + 4:i + 12])[0]; i += 12
        else:
            out[key] = b[i:i + 4].decode("latin-1"); i += 4
    return out


def to_xml(name, params, types, skip=("DisplayString",)):
    """Build the string pageItem.applyEffect() takes: <LiveEffect name="..."><Dict data="R key v I key v B key 1 "/></LiveEffect>"""
    code = {"Real": "R", "Int": "I", "Bool": "B", "String": "S", "UnicodeString": "U"}
    parts = []
    for k, v in params.items():
        t = types.get(k)
        if k in skip or " " in k or t not in ("Real", "Int", "Bool"):
            continue
        if t == "Bool":
            v = 1 if v else 0
        parts.append(f"{code[t]} {k} {v}")
    return f'<LiveEffect name="{name}"><Dict data="{" ".join(parts)} "/></LiveEffect>'


def sections(path):
    t = art_text(path)

    def between(a, b):
        i = t.find(a)
        j = t.find(b, i + 1)
        return t[i:j] if i >= 0 and j > i else ""
    return {"palette": between("%AI5_BeginPalette", "%AI5_EndPalette"),
            "layers": t[t.find("%AI5_BeginLayer"):],
            "setup": between("%%BeginSetup", "%%EndSetup")}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    cmd, f = sys.argv[1], sys.argv[2]
    if cmd == "effects":
        print(json.dumps(effects(f), ensure_ascii=False, indent=1))
    elif cmd == "hash":
        print(art_hash(f))
    elif cmd == "text":
        print(art_text(f))
    elif cmd == "grep":
        for line in art_text(f).splitlines():
            if re.search(sys.argv[3], line):
                print(line)

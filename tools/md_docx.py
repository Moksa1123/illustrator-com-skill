"""Markdown (the subset our sheets use: # ## ###, tables, - lists, > quotes, **bold**, `code`, [links](url)) -> formal DOCX,
then PDF through Word so pagination is Word's: table header rows repeat, rows never split, headings keep with next,
each "## N." chapter can start on a new page.

python tools/md_docx.py <in.md> [--title "..."] [--subtitle "..."]  -> <in>.docx + <in>.pdf
"""
import re
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

FONT = "微軟正黑體"
INK = RGBColor(0x1D, 0x1D, 0x1F)
GREY = RGBColor(0x6E, 0x6E, 0x73)


def set_font(run, size=None, bold=None, color=None):
    run.font.name = FONT
    run._r.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), FONT)
    if size:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color


def inline(par, text, size=10.5, color=INK, bold=False):
    """**bold**, `code`, [text](url) -> runs (links keep their text, url in grey)."""
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: m.group(1) + (f"（{m.group(2)}）" if m.group(2).startswith("http") else ""), text)
    for part in re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", text):
        if not part:
            continue
        if part.startswith("**"):
            set_font(par.add_run(part[2:-2]), size, True, color)
        elif part.startswith("`"):
            r = par.add_run(part[1:-1])
            set_font(r, size - 0.5, bold, RGBColor(0x0A, 0x3D, 0x91))
        else:
            set_font(par.add_run(part), size, bold, color)


def shade(cell, hex_):
    tcPr = cell._tc.get_or_add_tcPr()
    s = OxmlElement("w:shd")
    s.set(qn("w:val"), "clear")
    s.set(qn("w:color"), "auto")
    s.set(qn("w:fill"), hex_)
    tcPr.append(s)


def row_rules(row, header=False):
    trPr = row._tr.get_or_add_trPr()
    c = OxmlElement("w:cantSplit")                             # never break a row across pages
    trPr.append(c)
    if header:
        h = OxmlElement("w:tblHeader")                         # repeat on every page
        trPr.append(h)


def keep_next(par):
    par.paragraph_format.keep_with_next = True


def build(md_path, title=None, subtitle=None, chapter_breaks=True):
    md = Path(md_path).read_text(encoding="utf-8").split("\n")
    doc = Document()
    sec = doc.sections[0]
    sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)
    sec.top_margin = sec.bottom_margin = Cm(2.0)
    sec.left_margin = sec.right_margin = Cm(2.0)
    st = doc.styles["Normal"]
    st.font.name = FONT
    st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    st.font.size = Pt(10.5)
    st.paragraph_format.space_after = Pt(4)
    st.paragraph_format.line_spacing = 1.25
    # footer: page numbers
    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for kind, txt in (("begin", None), ("instr", "PAGE"), ("end", None)):
        r = fp.add_run()
        if kind == "instr":
            it = OxmlElement("w:instrText")
            it.text = txt
            r._r.append(it)
        else:
            f = OxmlElement("w:fldChar")
            f.set(qn("w:fldCharType"), kind)
            r._r.append(f)
        set_font(r, 9, color=GREY)
    i, first_chapter = 0, True
    while i < len(md):
        line = md[i]
        if line.startswith("# "):
            p = doc.add_paragraph()
            inline(p, title or line[2:], 20, INK, True)
            p.paragraph_format.space_after = Pt(2)
            if subtitle:
                q = doc.add_paragraph()
                inline(q, subtitle, 10, GREY)
            bar = doc.add_paragraph()
            pPr = bar._p.get_or_add_pPr()
            bd = OxmlElement("w:pBdr")
            b = OxmlElement("w:bottom")
            for k, v in (("w:val", "single"), ("w:sz", "12"), ("w:space", "1"), ("w:color", "1D1D1F")):
                b.set(qn(k), v)
            bd.append(b)
            pPr.append(bd)
        elif line.startswith("## "):
            if chapter_breaks and not first_chapter and re.match(r"## \d+\.", line) and int(re.match(r"## (\d+)", line).group(1)) in (4, 6, 9):
                doc.add_page_break()
            first_chapter = False
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
            inline(p, line[3:], 14, INK, True)
            keep_next(p)
        elif line.startswith("### "):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            inline(p, line[4:], 12, INK, True)
            keep_next(p)
        elif line.startswith("|"):
            rows = []
            while i < len(md) and md[i].startswith("|"):
                cells = [c.strip() for c in md[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            i -= 1
            n = max(len(r) for r in rows)
            t = doc.add_table(rows=0, cols=n)
            t.style = "Table Grid"
            t.alignment = WD_TABLE_ALIGNMENT.CENTER
            for ri, r in enumerate(rows):
                row = t.add_row()
                row_rules(row, header=ri == 0)
                for ci in range(n):
                    cell = row.cells[ci]
                    cell.paragraphs[0].paragraph_format.space_after = Pt(0)
                    inline(cell.paragraphs[0], (r[ci] if ci < len(r) else ""), 9.5, INK, ri == 0)
                    if ri == 0:
                        shade(cell, "EDEDF0")
            # column widths by content (17 cm text width), first column never squeezed into vertical text
            lens = [max(len(re.sub(r"[*`]", "", (r[ci] if ci < len(r) else ""))) for r in rows) for ci in range(n)]
            lens = [min(max(l, 4), 60) for l in lens]
            tot = sum(lens)
            widths = [max(Cm(17.0 * l / tot), Cm(2.6 if ci == 0 else 2.0)) for ci, l in enumerate(lens)]
            scale = Cm(17.0) / sum(widths)
            t.autofit = False
            for ci, w in enumerate(widths):
                for row in t.rows:
                    row.cells[ci].width = int(w * scale)
            doc.add_paragraph().paragraph_format.space_after = Pt(2)
        elif line.startswith("> "):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.6)
            inline(p, line[2:], 9.5, GREY)
        elif re.match(r"\s*- ", line):
            depth = (len(line) - len(line.lstrip())) // 2
            p = doc.add_paragraph(style="List Bullet" if depth == 0 else "List Bullet 2")
            txt = line.strip()[2:]
            txt = txt.replace("[x]", "☑").replace("[ ]", "☐")
            inline(p, txt)
        elif line.strip():
            p = doc.add_paragraph()
            inline(p, line)
        i += 1
    out = Path(md_path).with_suffix(".docx")
    doc.save(out)
    return out


def to_pdf(docx_path, pdf=None):
    pdf = Path(pdf) if pdf else Path(docx_path).with_suffix(".pdf")
    ps = (f"$w = New-Object -ComObject Word.Application; $w.Visible = $false; $d = $w.Documents.Open('{Path(docx_path).as_posix()}'); "
          f"$d.ExportAsFixedFormat('{pdf.as_posix()}', 17); $d.Close(0); $w.Quit(); 'ok'")
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True)
    return pdf


if __name__ == "__main__":
    a = sys.argv[1:]
    title = a[a.index("--title") + 1] if "--title" in a else None
    sub = a[a.index("--subtitle") + 1] if "--subtitle" in a else None
    d = build(a[0], title, sub)
    pdf = a[a.index("--pdf") + 1] if "--pdf" in a else None
    print(d, to_pdf(d, pdf))

"""Re-file a logo package (tools/logo_package.py output) into a clean, use-first delivery folder, and add a trademark folder.

<Brand>_Brand-Assets/
  00_README.md
  01_Print_印刷用/<layout>/<variant>/  .ai .eps .pdf        (CMYK / spot)
  02_Digital_數位用/SVG/  PNG/<layout>/<tone>/  JPG/
  03_Social_社群/  Avatar_頭像/ Cover_封面/ Share_分享圖/ Email_簽名/
  04_Web-App_網站/
  05_Business-Card_名片/
  06_Guidelines_品牌規範/
  07_Source_原始檔/        editable RGB .ai
  08_Trademark_商標申請/   trademark drawings (JPG + TIF, 300 dpi, 5-8 cm) + the filing sheet
Filenames: <brand>_<layout>_<tone>[_<size>].<ext>  (ASCII only: safe for printers, zip tools and every OS)

python tools/brand_assets.py <brand config.json> <trademark sheet .md>
"""
import json
import re
import shutil
import sys
from pathlib import Path

from PIL import Image


def clean(dst):
    if dst.exists():
        for f in sorted(dst.rglob("*"), key=lambda p: -len(p.parts)):
            try:
                f.unlink() if f.is_file() else f.rmdir()
            except OSError:
                pass
    dst.mkdir(parents=True, exist_ok=True)


def cp(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return dst


def build(cfg, sheet=None):
    C = json.loads(Path(cfg).read_text(encoding="utf-8"))
    pkg, slug = Path(C["out"]), C["slug"]
    dst = Path(C["assets"])
    clean(dst)
    LAY = C["layout_names"]            # stem -> clean layout label
    TONE = C["tone_names"]             # suffix -> clean tone label
    PRINT = C["print_names"]           # print set -> clean variant label
    moved = []
    # 01 print: <layout>/<variant>/<brand>_<layout>_<variant>_<CMYK|SPOT>.<ext>
    for f in sorted((pkg / "02_print_CMYK").iterdir()):
        m = re.match(r"(.+?)_(.+?)(_CMYK)?\.(ai|eps|pdf)$", f.name)
        if not m:
            continue
        stem, pset, cm, ext = m.groups()
        if stem not in LAY or pset not in PRINT:
            continue
        lay, var = LAY[stem], PRINT[pset]
        space = "CMYK" if cm else "SPOT"
        moved.append(cp(f, dst / "01_Print_印刷用" / lay / var / f"{slug}_{lay}_{var}_{space}.{ext}"))
    # 02 digital: SVG, PNG/<layout>/<tone>/, JPG
    for f in sorted((pkg / "01_vector_RGB").glob("*_RGB.svg")):
        stem, sfx = split_tone(f.name[:-len("_RGB.svg")], LAY, TONE)
        if stem:
            moved.append(cp(f, dst / "02_Digital_數位用" / "SVG" / f"{slug}_{LAY[stem]}_{TONE[sfx]}.svg"))
    for f in sorted((pkg / "03_screen_PNG_JPG").glob("*.png")):
        m = re.match(r"(.+)_RGB_(\d+)(px|w)\.png$", f.name)
        if not m:
            continue
        stem, sfx = split_tone(m.group(1), LAY, TONE)
        if stem:
            size = f"{m.group(2)}x{m.group(2)}" if m.group(3) == "px" else f"{m.group(2)}w"
            moved.append(cp(f, dst / "02_Digital_數位用" / "PNG" / LAY[stem] / TONE[sfx] / f"{slug}_{LAY[stem]}_{TONE[sfx]}_{size}.png"))
    for f in sorted((pkg / "03_screen_PNG_JPG").glob("*.jpg")):
        m = re.match(r".+_on-(white|dark)_RGB_(\d+)px\.jpg$", f.name)
        if m:
            moved.append(cp(f, dst / "02_Digital_數位用" / "JPG" / f"{slug}_primary_on-{m.group(1)}_{m.group(2)}x{m.group(2)}.jpg"))
    # 03 social
    for f in sorted((pkg / "04_social").glob("*.png")):
        n = f.name[len(slug) + 1:]
        sub = ("Avatar_頭像" if n.startswith("avatar") else "Share_分享圖" if n.startswith("open-graph") else
               "Email_簽名" if n.startswith("email") else "Cover_封面")
        moved.append(cp(f, dst / "03_Social_社群" / sub / f"{slug}_{n}"))
    # 04 web / app
    for f in sorted((pkg / "05_favicon_app").iterdir()):
        if f.is_file():
            moved.append(cp(f, dst / "04_Web-App_網站" / f.name))
    # 05 card, 06 guidelines
    for f in sorted((pkg / "06_print_collateral").iterdir()):
        if f.is_file():
            n = f.name.replace("-print.pdf", "_PRINT_PDF-X1a.pdf").replace("-front.png", "_preview-front.png").replace("-back.png", "_preview-back.png")
            moved.append(cp(f, dst / "05_Business-Card_名片" / n))
    for f in sorted((pkg / "07_guidelines").iterdir()):
        if f.is_file() and f.suffix in (".pdf", ".png"):
            moved.append(cp(f, dst / "06_Guidelines_品牌規範" / f.name))
    # 07 source: editable RGB .ai
    for f in sorted((pkg / "01_vector_RGB").glob("*_RGB.ai")):
        stem, sfx = split_tone(f.name[:-len("_RGB.ai")], LAY, TONE)
        if stem:
            moved.append(cp(f, dst / "07_Source_原始檔" / f"{slug}_{LAY[stem]}_{TONE[sfx]}_RGB-editable.ai"))
    # PNG resolution tag: 300 ppi (pixels unchanged) so print shops / Office read the real print size (4096 px = 34.7 cm)
    for f in (dst / "02_Digital_數位用" / "PNG").rglob("*.png"):
        im = Image.open(f)
        im.load()
        im.save(f, dpi=(300, 300))
    # 08 trademark drawings: 300 dpi, 5-8 cm (TIPO) -> 900 px = 7.62 cm; JPG + TIF, flattened on white
    tm = dst / "08_Trademark_商標申請"
    tm.mkdir(parents=True, exist_ok=True)
    for label, spec in C["trademark"].items():
        src = pkg / spec["src"]
        im = Image.open(src).convert("RGBA")
        im = im.crop(im.getchannel("A").getbbox())          # drawing = the mark itself, no clear-space padding
        side = 900
        canvas = Image.new("RGB", (side, side), (255, 255, 255))
        w, h = im.size
        k = min(side * spec.get("fill", 0.86) / w, side * spec.get("fill", 0.86) / h)
        im2 = im.resize((round(w * k), round(h * k)), Image.LANCZOS)
        canvas.paste(im2, ((side - im2.size[0]) // 2, (side - im2.size[1]) // 2), im2)
        if spec.get("gray"):
            canvas = canvas.convert("L")
        for ext in ("jpg", "tif"):
            out = tm / f"{slug}_trademark_{label}_300dpi_7.6cm.{ext}"
            canvas.save(out, dpi=(300, 300), quality=95) if ext == "jpg" else canvas.save(out, dpi=(300, 300), compression="tiff_lzw")
            moved.append(out)
    for label, spec in C.get("wordmark", {}).items():                   # plain word-mark drawing
        from PIL import ImageDraw, ImageFont
        font = ImageFont.truetype(spec["font"], spec.get("size", 150))
        canvas = Image.new("L", (900, 900), 255)
        d = ImageDraw.Draw(canvas)
        bb = d.textbbox((0, 0), spec["text"], font=font)
        d.text(((900 - (bb[2] - bb[0])) / 2 - bb[0], (900 - (bb[3] - bb[1])) / 2 - bb[1]), spec["text"], fill=0, font=font)
        for ext in ("jpg", "tif"):
            out = tm / f"{slug}_trademark_{label}_300dpi_7.6cm.{ext}"
            canvas.save(out, dpi=(300, 300), quality=95) if ext == "jpg" else canvas.save(out, dpi=(300, 300), compression="tiff_lzw")
            moved.append(out)
    # paper filing: TIPO asks for 5 floating drawings (5-8 cm) on plain paper -> A4 sheet, 6 copies at 7.62 cm, 300 dpi, cut guides
    from PIL import ImageDraw, ImageFont
    for jpg in sorted(tm.glob("*_trademark_*.jpg")):
        page = Image.new("RGB", (2480, 3508), (255, 255, 255))
        d = ImageDraw.Draw(page)
        cell = Image.open(jpg).convert("RGB")
        xs, ys = (295, 1285), (330, 1380, 2430)
        for y in ys:
            for x in xs:
                page.paste(cell, (x, y))
                for k in range(0, 900, 30):                     # dashed cut frame, 3 mm outside the drawing
                    for (a, b, c2, e) in ((x - 35 + k, y - 35, x - 35 + k + 15, y - 35), (x - 35 + k, y + 935, x - 35 + k + 15, y + 935),
                                          (x - 35, y - 35 + k, x - 35, y - 35 + k + 15), (x + 935, y - 35 + k, x + 935, y - 35 + k + 15)):
                        d.line((a, b, c2, e), fill=(150, 150, 150), width=2)
        try:
            f = ImageFont.truetype("C:/Windows/Fonts/msjh.ttc", 38)
        except OSError:
            f = None
        d.text((295, 3380), f"浮貼用商標圖樣 5 張以上（每張 7.62 × 7.62 cm，300 dpi）· 列印請選「實際大小／100%」· {jpg.stem}", fill=(90, 90, 90), font=f)
        out = tm / "paper-filing_浮貼用" / f"{jpg.stem}_A4-print.pdf"
        out.parent.mkdir(exist_ok=True)
        page.save(out, "PDF", resolution=300)
        moved.append(out)
    if sheet:                                                  # the filing sheet: editable DOCX + formal PDF (Word layout); the .md source stays in _work
        sp = Path(sheet)
        formal = sp.with_name(sp.stem + "_正式版.pdf")
        for src, name in ((sp.with_suffix(".docx"), sp.stem + ".docx"), (formal if formal.exists() else sp.with_suffix(".pdf"), sp.stem + ".pdf")):
            if src.exists():
                cp(src, tm / name)
        forms = sp.parent / "tipo_forms" / "filled"             # TIPO official application forms, filled (T0101)
        if forms.exists():
            for f in sorted(forms.iterdir()):
                if f.suffix in (".docx", ".pdf"):
                    moved.append(cp(f, tm / "application-form_官方申請書" / f.name))
    readme(C, dst)
    return dst, moved


def split_tone(base, LAY, TONE):
    for stem in sorted(LAY, key=len, reverse=True):          # longest layout stem first (logo-horizontal before logo)
        if base.startswith(stem):
            sfx = base[len(stem):]
            if sfx in TONE:
                return stem, sfx
    return None, None


def readme(C, dst):
    def count(p):
        return sum(1 for f in p.rglob("*") if f.is_file())
    L = [f"# {C['name']} 品牌資產 Brand Assets", "",
         "由 Adobe Illustrator 自向量母檔產出，並經程式逐檔檢查（尺寸、印刷檔僅含 CMYK／專色、灰色皆為單 K）。", "",
         "## 我要用在哪裡？", "",
         "| 用途 | 開這個資料夾 | 用哪個檔 |", "|---|---|---|",
         "| **送印刷廠**（名片、包裝、貼紙、招牌） | `01_Print_印刷用` | `.pdf`（PDF/X-1a）或 `.eps`；燙金／燙銀用 `spot` 版 |",
         "| 網站、簡報、文件 | `02_Digital_數位用/SVG` | `.svg`（任何尺寸都清晰） |",
         "| 需要圖片檔（LINE、Word、剪輯） | `02_Digital_數位用/PNG` | 依版型 → 淺底／深底 → 尺寸（去背） |",
         "| 社群大頭貼、封面、分享圖 | `03_Social_社群` | 檔名含平台與尺寸 |",
         "| 網站 favicon / App 圖示 | `04_Web-App_網站` | 附 `head-snippet.html` |",
         "| 名片送印 | `05_Business-Card_名片` | `_PRINT_PDF-X1a.pdf`（出血 3 mm） |",
         "| 品牌使用規範 | `06_Guidelines_品牌規範` | `.pdf` |",
         "| 設計師要修改 | `07_Source_原始檔` | `.ai`（RGB 可編輯） |",
         "| **商標申請** | `08_Trademark_商標申請` | 先讀 `商標申請資料表.md` |", "",
         "## 版型與色彩版本", "", "| 名稱 | 意思 |", "|---|---|"]
    L += [f"| `{v}` | {d} |" for v, d in C["glossary"]]
    L += ["", "## 資料夾內容", "", "| 資料夾 | 檔案數 |", "|---|---|"]
    L += [f"| {p.name} | {count(p)} |" for p in sorted(dst.iterdir()) if p.is_dir()]
    L += ["", "## 解析度（300 dpi）", "",
          "- **印刷檔（`01_Print`、名片）是純向量**：不含任何點陣圖，放大到任何尺寸都清晰，不受 dpi 限制，送印一律用這些。",
          "- **PNG 皆標記 300 dpi**，像素對應的 300 dpi 印刷尺寸：", "",
          "| 像素 | 300 dpi 印刷尺寸 | 適合 |", "|---|---|---|",
          "| 4096 px | 34.7 cm | 海報、展板（仍建議用向量 PDF） |", "| 2048 px | 17.3 cm | A4 文件、包裝貼紙 |",
          "| 1024 px | 8.7 cm | 名片、吊牌、小貼紙 |", "| 512 px | 4.3 cm | 網站、簡報 |", "",
          "- **商標圖樣**（`08_Trademark`）：300 dpi、900 × 900 px ＝ 7.62 cm，符合智慧局 5–8 cm 規定。", ""]
    L += ["", "## 色彩規格", "", "| 色彩 | 螢幕 (HEX) | 印刷 (CMYK) | 特別色 |", "|---|---|---|---|"]
    L += [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in C["colors"]]
    L += ["", "特別色以金屬 Pantone 名稱標示（檔案內含 CMYK 替代值），正式印製前請以印刷廠實體色票確認油墨／燙箔。", ""]
    (dst / "00_README.md").write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    dst, moved = build(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(dst, len(moved), "files")

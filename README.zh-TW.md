# illustrator-com-skill

[English](README.md) · **繁體中文**

讓程式代理（Claude Code 等）在 **Windows 上操作 Adobe Illustrator**。每一項能力都在沙盒文件裡實際執行，並且**讀回結果**驗證——
讀 DOM 的值、讀匯出的像素、讀 Illustrator 實際存進檔案的效果參數——不靠猜。

與 [photoshop-com-skill](https://github.com/Moksa1123/photoshop-com-skill) 同一套原則。

## 內容

| 部分 | 做什麼 |
|---|---|
| `lib/ai_run.py` | 透過 COM 執行 ExtendScript 並回傳結果。COM 型別庫沒註冊（`TYPE_E_LIBNOTREGISTERED`）也能用，不會跳「是否執行指令碼」；**自動處理 Illustrator 的對話框**：取消（預設，永不卡住）、按確定、或填入欄位（`["sel", "type:30", "tab", "ok"]`）。偵測並復原當掉的指令碼引擎。 |
| `lib/ailib.jsx` | 經過測試的設計函式庫，座標以工作區域左上角為原點：形狀與 SVG 路徑、RGB／CMYK／特別色／漸層、筆畫樣式、混合樣式文字、路徑文字、字級自動縮放、字元／段落樣式、保留樣式的尋找取代、路徑管理員（聯集、減去上層、交集、差集、分割、剪裁、合併、裁切、外框、減去下層）、對齊／均分／格狀排列、剪裁遮色片、複合路徑、符號、繪圖樣式、重複、漸變、置入／嵌入／影像描圖／點陣化、重新上色、含安全區參考線的新文件，以及 PNG／JPG／WebP／SVG／PDF／PSD／轉存為螢幕適用。 |
| `presets/effects.json` | **效果選單每一個效果都能不開對話框套用**（`applyEffect` XML：陰影、光暈、彎曲、3D 與材質、Photoshop 濾鏡…），預設參數與型別都是從 Illustrator 自己存的檔案讀回來的。 |
| `lib/fingerprint.jsx`、`tools/ai_dump.py` | 文件指紋（DOM 每一部分），以及未壓縮 `.ai` 讀取器：找回 DOM 看不到的東西——即時效果與全部參數（含 Photoshop 濾鏡的二進位描述），以及穩定的圖稿雜湊。 |
| `index/` | **從你自己的 Illustrator 建立**的 API 索引（`ScriptingSupport.aip` 內的型別庫＋執行期反射）、從鍵盤快捷鍵組合擷取的完整選單指令表、查詢工具（`find`、`class`、`enum`、`member`、`menu`、`effect`、`stats`）。 |
| `tests/` | 函式庫測試（`run_tests.py` → `REPORT.md`），以及每個選單指令、效果、工具的掃描（`menu_sweep.py`、`effects_sweep.py`、`tools_sweep.py`）→ `CAPABILITIES.md`：每一項怎麼用腳本做、怎麼驗證的。 |
| `presets/sizes.json` + `tools/sizes.py` | 53 種設計尺寸（IG、FB、OG、LINE、YouTube、TikTok、Google Ads、Amazon、Shopify、Etsy、蝦皮、momo…），含安全區與出處；`new <id>` 直接開出工作區域與參考線。 |
| `tools/html2ai.py` | 固定尺寸 HTML 版面 → **可編輯向量** Illustrator 文件：方塊變成形狀（填色、線性漸層、邊框、圓角、陰影），照片依畫面裁切後嵌入，內嵌 SVG 匯入成路徑，文字是真的文字物件。 |
| `tools/ui.py`、`tools/capture_commands.py`、`tools/make_graph_fixture.py` | 只對 Illustrator 視窗送出的螢幕／鍵盤操作，處理少數只存在於畫面上的功能。 |

## 驗證覆蓋率（Illustrator 2024 / 28.0）

<!-- coverage:start -->
- **選單指令：可腳本化的設計指令 452/452 全部驗證（100.0%）；連同 2 個被 Illustrator 擋下的指令為 452/454（99.6%）。** 另有 181 個是介面／偏好設定／網路／生成式 AI 指令（n/a，每個都附原因）。每個 ✅ 都在沙盒文件中實際執行並讀回結果。
- **效果：115/115** 個「效果」選單效果以 LiveEffect XML 免對話框套用，所有參數從存檔讀回（`presets/effects.json`）。
- **函式庫：39/40** 項測試通過（`tests/REPORT.md`）：DOM 讀回、匯出像素、匯出檔解碼、存檔效果。
- **工具：60/85** 個工具可切換並讀回；其餘 `selectTool` 接受但 Illustrator 的 `getSelectedToolName()` 會拋錯（每個都有對應的腳本做法）。
- 被擋下（證據在 `tests/blocked.json`）：File > Save Selected Slices；File > Print。

| Menu | ✅ | blocked | n/a |
|---|---|---|---|
| File | 21 | 2 | 3 |
| Edit | 25 | 0 | 29 |
| Object | 124 | 0 | 5 |
| Type | 48 | 0 | 7 |
| Select | 39 | 0 | 0 |
| Effect | 119 | 0 | 0 |
| View | 40 | 0 | 45 |
| Window | 1 | 0 | 63 |
| Help | 0 | 0 | 7 |
| Keyboard | 35 | 0 | 22 |

每個指令的腳本做法與驗證方式：[tests/CAPABILITIES.md](tests/CAPABILITIES.md)。
<!-- coverage:end -->

## 安裝

```bash
pip install -r requirements.txt
playwright install chromium        # 只有 html2ai 需要
```

當作代理技能使用：把整個資料夾複製到技能目錄（例如 `~/.claude/skills/illustrator-com/`）。

## 快速開始

```bash
python lib/ai_run.py -e "app.version"
python tests/run_tests.py                  # 你的 Illustrator 能做什麼 -> tests/REPORT.md
python index/build_index.py                # 從你的 Illustrator 建 API 索引
python index/ai_api.py menu 路徑管理員      # 或英文：menu pathfinder
python index/ai_api.py effect shadow       # 免對話框的效果 XML
python tools/sizes.py new ig_story_reel    # 1080x1920 工作區域＋安全區參考線
python tools/html2ai.py tests/fixtures/fixture.html out/card.ai --w 600 --h 800 --png out/card.png
```

## 原則

- **驗證，不假設。**「沒有錯誤」不是證據：在同一次呼叫中剛選取就下選單指令，會默默作用在舊的選取上；很多 DOM 寫入被忽略也不報錯；對話框沒關會卡住一切。`CAPABILITIES.md` 每一列都實際跑過並讀回。
- **對話框也是 API。** 只有對話框的指令就透過對話框操作（填欄位、按確定），而且只有 Illustrator 的那個對話框會收到按鍵。
- **不使用生成式 AI 功能**（生成式重新上色、文字轉圖樣、Mockup Beta）——與 Photoshop 技能相同政策。
- **尺寸會變。** 每個尺寸都附出處與查證日期，大檔期前請再確認。

## 需求

Windows 10/11、Python 3.9+。在 Illustrator 2024（28.0）開發並驗證；其他版本走同一套 COM 介面應可運作但未測試，請在你的版本上跑 `tests/run_tests.py` 與各項 sweep。

疑難排解：`docs/troubleshooting-com.md` · 尺寸：`docs/sizes.md`

## 授權

MIT，見 `LICENSE` 與 `NOTICE`。不散布任何 Adobe 文件或第三方索引；API 索引在你的電腦上從你安裝的 Illustrator 產生。

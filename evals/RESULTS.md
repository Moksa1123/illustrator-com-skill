# evals 結果

最新的在最上面。題目與評分標準見 `cases.json`，評分程式 `grade.py`。

## 2026-11-16 第 2 輪（現行題組，Illustrator 28.0.0 資料）

- 第 1 輪有 10 題沒 skill 也答對，換成 LiveEffect 冷門名稱與參數鍵、腳本被拒時的替代路線、索引統計等憑記憶答不出的題。
- 本輪另有 5 題沒 skill 也答對（`twist-effect-name`、`warp-flag-style`、`offset-path-effect-keys`、`point-area-route`、`rotate-view-route`），已標 `retired`，下表不列。

| 項目 | 有 skill | 沒有 skill |
|---|---|---|
| 計分題答對率（12 題） | **12/12（100.0%）** | 0/12（0.0%） |
| 全部題目（12 題） | 12/12 | 0/12 |
| 模型 | claude-opus-5-5 | claude-opus-5-5 |
| 作答方式 | subagent 讀 SKILL.md、用 ai_api.py 查 | subagent 不用任何工具，憑記憶作答 |
| 答案檔 | `evals/runs/2026-11-16-r2-with-skill.json` | `evals/runs/2026-11-16-r2-without-skill.json` |

| 題目 | 可信度 | 有 skill | 沒有 skill | 備註 |
|---|---|---|---|---|
| `pucker-effect-name` | 實測 | ✅ | ❌ |  |
| `zigzag-effect-keys` | 實測 | ✅ | ❌ |  |
| `blocked-menu-cmds` | 實測 | ✅ | ❌ |  |
| `repeat-config-null` | 實測 | ✅ | ❌ |  |
| `press-quality-bleed` | 實測 | ✅ | ❌ |  |
| `tweak-effect-name` | 實測 | ✅ | ❌ |  |
| `roughen-detail-key` | 實測 | ✅ | ❌ |  |
| `rasterize-effect-dpi-key` | 實測 | ✅ | ❌ |  |
| `outline-object-effect-name` | 實測 | ✅ | ❌ |  |
| `type-on-path-route` | 實測 | ✅ | ❌ |  |
| `unverified-member-count` | 實測 | ✅ | ❌ |  |
| `same-call-selection` | 實測 | ✅ | ❌ |  |

## 2026-11-16 第 1 輪（舊題組，大多淘汰）

沒有 skill 的模型憑記憶答對 10/15：常用選單指令的 executeMenuCommand 字串（`OffsetPath v22`、`Make Planet X`、`Selection Hat 5`…）、Feather／Gaussian Blur 的 LiveEffect 名稱、Drop Shadow 參數鍵模型本來就知道，沒有鑑別度，已在 `cases.json` 標 `retired`。

| 項目 | 有 skill | 沒有 skill |
|---|---|---|
| 計分題答對率（5 題） | **5/5（100.0%）** | 0/5（0.0%） |
| 全部題目（15 題） | 15/15 | 10/15 |
| 答案檔 | `evals/runs/2026-11-16-with-skill.json` | `evals/runs/2026-11-16-without-skill.json` |

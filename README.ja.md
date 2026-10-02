# illustrator-com-skill

[English](README.md) · [繁體中文](README.zh-TW.md) · **日本語** · [한국어](README.ko.md)

コーディングエージェント（Claude Code など）から **Windows 上の Adobe Illustrator** を操作するスキルです。すべての機能はサンドボックス文書で実際に実行し、
**結果を読み戻して**確認しています（DOM の値、書き出したピクセル、Illustrator が保存ファイルに実際に書き込んだ効果パラメーター）。推測はしません。

[photoshop-com-skill](https://github.com/Moksa1123/photoshop-com-skill) と同じ方針で作られています。

## 内容

| 部分 | 内容 |
|---|---|
| `lib/ai_run.py` | COM 経由で ExtendScript を実行して結果を返します。COM タイプライブラリ未登録（`TYPE_E_LIBNOTREGISTERED`）でも動作し、「スクリプトを実行しますか？」は表示されません。**Illustrator のモーダルダイアログに自動で応答**します：キャンセル（既定、固まらない）、OK、またはフィールド入力（`["sel", "type:30", "tab", "ok"]`）。スクリプトエンジンの異常も検出して復旧します。 |
| `lib/ailib.jsx` | アートボード左上原点で使えるテスト済みデザインライブラリ：図形と SVG パス、RGB／CMYK／特色／グラデーション、線のスタイル、混在スタイルのテキスト、パス上文字、文字の自動フィット、文字／段落スタイル、スタイルを保った検索と置換、パスファインダー（合体、前面オブジェクトで型抜き、交差、中マド、分割、刈り込み、合流、切り抜き、アウトライン、背面オブジェクトで型抜き）、整列／分布／グリッド、クリッピング、複合パス、シンボル、グラフィックスタイル、リピート、ブレンド、配置／埋め込み／画像トレース／ラスタライズ、再配色、セーフゾーンガイド付き新規文書、PNG／JPG／WebP／SVG／PDF／PSD／スクリーン用に書き出し。 |
| `presets/effects.json` | **「効果」メニューのすべての効果をダイアログなしの `applyEffect` XML で**（ドロップシャドウ、光彩、ワープ、3D とマテリアル、Photoshop フィルター…）。既定パラメーターと型は Illustrator 自身の保存ファイルから読み戻したものです。 |
| `lib/fingerprint.jsx`、`tools/ai_dump.py` | 文書フィンガープリント（DOM の全要素）と非圧縮 `.ai` リーダー。DOM から見えないもの（全パラメーター付きのライブ効果、Photoshop フィルターのバイナリ記述子、安定したアートハッシュ）を取り出します。 |
| `index/` | **お使いの Illustrator から生成する** API インデックス（`ScriptingSupport.aip` 内のタイプライブラリ＋実行時リフレクション）、キーボードショートカットから取得した全メニューコマンド一覧、検索ツール（`find`、`class`、`enum`、`member`、`menu`、`effect`、`stats`）。 |
| `tests/` | ライブラリテスト（`run_tests.py` → `REPORT.md`）と、全メニューコマンド・効果・ツールのスイープ（`menu_sweep.py`、`effects_sweep.py`、`tools_sweep.py`）→ `CAPABILITIES.md`：それぞれのスクリプトでの実行方法と検証方法。 |
| `presets/sizes.json` + `tools/sizes.py` | 54 種のデザインサイズ（Instagram、Facebook、Open Graph、LINE、YouTube、TikTok、Google 広告、Amazon、Shopify、Etsy、Shopee、momo…）、セーフゾーンと出典付き。`new <id>` でガイド付きアートボードを作成します。 |
| `tools/html2ai.py` | 固定サイズの HTML レイアウト → **編集可能なベクター**の Illustrator 文書：ボックスは図形（塗り、線形グラデーション、枠線、角丸、影）、写真は表示どおりに埋め込み、インライン SVG はパス、テキストは本物のテキストフレームになります。 |
| `tools/logo_package.py`、`tools/brand_assets.py` | 完成したロゴ素材（JSON 設定 1 つ）から業界標準の**ロゴ納品パッケージ**を生成：RGB ベクター、そのまま入稿できる CMYK AI／EPS／PDF-X-1a（グレーは K 単色、ブランドインキの K 値、特色版、ファイルごとの色監査）、PNG 64–4096 px（300 ppi）、SNS アイコン／カバー／OGP／メール、favicon とアプリアイコン。さらに用途別の整理されたフォルダー（印刷／デジタル／SNS／Web／名刺／ガイドライン／ソース／商標）に再配置します。 |
| `tools/tipo_form.py`、`tools/md_docx.py` | 台湾知的財産局（TIPO）への商標出願補助：商標見本（JPG＋TIF、300 dpi、7.6 cm）、公式 T0101 出願書類の記入（チェック欄は書式の枠そのものに記入）、Markdown → Word 経由の正式な DOCX／PDF（表のヘッダー行を各ページで繰り返し、行を分割しない）。 |
| `tools/ui.py`、`tools/capture_commands.py`、`tools/make_graph_fixture.py` | 画面上にしかない少数の機能のための、Illustrator ウィンドウ限定の画面／キーボード操作。 |

## 検証カバレッジ（Illustrator 2024 / 28.0）

<!-- coverage:start -->
- **メニューコマンド：スクリプト可能なデザインコマンド 452/452 をすべて検証（100.0%）。Illustrator にブロックされる 2 件を含めると 452/454（99.6%）。** 残り 181 件は UI／環境設定／Web／生成 AI のコマンド（n/a、理由はコマンドごとに記載）。✅ はすべてサンドボックス文書で実行し、結果を読み戻して確認しています。
- **効果：115/115** 件の「効果」メニューの効果を LiveEffect XML でダイアログなしに適用し、全パラメーターを保存ファイルから読み戻し（`presets/effects.json`）。
- **ライブラリ：40/40** 件のテストに合格（`tests/REPORT.md`）：DOM の読み戻し、書き出したピクセル、書き出しファイルのデコード、保存ファイルの効果。
- **ツール：60/85** 件を選択して読み戻し。残りは `selectTool` は受け付けるものの `getSelectedToolName()` が例外を投げます（いずれもスクリプトでの代替手段あり）。
- ブロック（証拠は `tests/blocked.json`）：File > Save Selected Slices、File > Print。

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

コマンドごとのスクリプトでの実行方法と検証方法：[tests/CAPABILITIES.md](tests/CAPABILITIES.md)。
<!-- coverage:end -->

## インストール

Windows 10/11、Adobe Illustrator、Python 3.9+、Node 18+ が必要です。

```bash
npm install -g illustrator-com-skill
illustrator-com init --ai claude -g      # または：npx illustrator-com-skill init --ai claude -g
illustrator-com setup                    # pip install -r requirements.txt＋お使いの Illustrator から API インデックス＋doctor
```

`init` は実行環境（`lib/`、`tools/`、`index/`、`tests/`、`presets/`）を `~/.illustrator-com-skill/` に一度だけコピーし、
各アシスタントにそれを指す `SKILL.md` を書き込みます。お使いの Illustrator から作る API インデックスは一度作ればすべてのアシスタントで共有され、更新しても消えません。

```bash
illustrator-com init                       # アシスタントを対話式に選択
illustrator-com init --ai cursor,windsurf  # このプロジェクトのみ（.cursor/skills/…、.windsurf/skills/…）
illustrator-com init --ai all -g           # ユーザー全体の skills フォルダーを持つすべてのアシスタント
illustrator-com doctor --smoke             # Windows、Python、パッケージ、Illustrator COM、インデックス、実スクリプト 1 本
illustrator-com list | info | versions | uninstall [--purge]
```

### 14 の AI プラットフォーム

| `--ai` | アシスタント | プロジェクト | グローバル（`-g`） |
|---|---|---|---|
| `claude` | Claude Code | `.claude/skills/illustrator-com/` | `~/.claude/skills/` |
| `cursor` | Cursor | `.cursor/skills/illustrator-com/` | `~/.cursor/skills/` |
| `windsurf` | Windsurf / Devin Desktop | `.windsurf/skills/illustrator-com/` | — |
| `antigravity` | Antigravity／汎用エージェント | `.agent/skills/illustrator-com/` | `~/.gemini/antigravity/global_skills/` |
| `copilot` | GitHub Copilot | `.github/skills/illustrator-com/` | `~/.copilot/skills/` |
| `kiro` | Kiro | `.kiro/skills/illustrator-com/` | — |
| `codex` | Codex CLI | `.codex/skills/illustrator-com/` | `~/.codex/skills/` |
| `qoder` | Qoder | `.qoder/skills/illustrator-com/` | — |
| `cline` | Cline | `.cline/skills/illustrator-com/` | `~/.cline/skills/` |
| `gemini` | Gemini CLI | `.gemini/skills/illustrator-com/` | `~/.gemini/skills/` |
| `trae` | Trae | `.trae/skills/illustrator-com/` | — |
| `opencode` | OpenCode | `.opencode/skills/illustrator-com/` | — |
| `continue` | Continue | `.continue/skills/illustrator-com/` | — |
| `codebuddy` | CodeBuddy | `.codebuddy/skills/illustrator-com/` | — |

アシスタントは Illustrator がインストールされた Windows マシン上で動かす必要があります。クラウドエージェント（Claude.ai Web、Copilot coding agent、Codex cloud）からローカルの Illustrator には届きません。

### 更新

```bash
illustrator-com update                   # npm の最新版 → 実行環境と記録済みのすべてのインストール
illustrator-com check                    # 新しい版があるか（結果は 24 時間キャッシュ）
illustrator-com config auto-update on    # check が新版を見つけたら自動でインストール
```

インストールされた各 `SKILL.md` は、セッション開始時に `check --quiet` を一度実行するようエージェントに指示するので、新版が出れば自然に通知されます。
自動更新は**既定でオフ**です。オンにしない限り、作業の途中で版が変わることはありません。更新しても API インデックス（`index/ai-dom.json`）は保持され、
編集した実行環境のファイルは `~/.illustrator-com-skill/_state/backup/` にバックアップされます。

スキル自体を開発する場合：`node bin/illustrator-com.mjs init --link --ai claude -g` で、実行環境をコピーではなくチェックアウトに向けます。

## クイックスタート

```bash
python lib/ai_run.py -e "app.version"
python tests/run_tests.py                  # お使いの Illustrator で動くもの -> tests/REPORT.md
python index/build_index.py                # お使いの Illustrator から API インデックス
python index/ai_api.py find gradient stop
python index/ai_api.py menu pathfinder     # メニューコマンドと検証状況
python index/ai_api.py effect shadow       # ダイアログなしの効果 XML
python tools/sizes.py new ig_story_reel    # セーフゾーンガイド付き 1080x1920 アートボード
python tools/html2ai.py tests/fixtures/fixture.html out/card.ai --w 600 --h 800 --png out/card.png
```

```python
import sys; sys.path.insert(0, "lib")
from ai_run import run_js
from ailib_loader import library
run_js(library() + """
AI.newDoc(1080, 1080, 'post', {bg: '#f4f2ee', safe: [60, 60, 60, 60]});
var card = AI.roundRect(90, 90, 900, 900, 40, {fill: AI.gradient([[0, '#c8a97e'], [1, '#8c6f52']], {angle: 90}), stroke: null});
AI.dropShadow(card, {y: 10, blur: 14, opacity: 0.3});
AI.text('Bean & Heart', 140, 160, {font: 'Georgia-Italic', size: 110, color: '#2b2520'});
var badge = AI.pathfinder([AI.circle(880, 880, 90), AI.star(880, 880, 60, 25, 5)], 'minusFront');
AI.style(badge, {fill: '#2b2520', stroke: null});
AI.png('C:/out/post.png'); AI.svg('C:/out/post.svg', {outlineText: true}); 'ok'
""")
```

## 方針

- **推測せず検証する。**「エラーなし」は証拠になりません。選択と同じ呼び出しで出したメニューコマンドは古い選択に作用し、多くの DOM 書き込みはエラーなしで無視され、
  開いたままのダイアログはすべてを止めます。`CAPABILITIES.md` の各行は実行して読み戻したものです。
- **ダイアログも API の一部。** ダイアログしかないコマンドはダイアログ経由で操作します（入力して OK）。キー入力を受け取るのは Illustrator のダイアログウィンドウだけです。
- **生成 AI 機能は使いません**（生成再配色、テキストからパターン、モックアップ β）— Photoshop スキルと同じ方針です。
- **サイズは変わります。** 各プリセットには出典と確認日があります。大きなキャンペーンの前に再確認してください。

## 動作環境

Windows 10/11、Python 3.9+、Node 18+（インストーラーのみ）。Illustrator 2024（28.0）で開発・検証しています。他の版も同じ COM インターフェースで動くはずですが未検証なので、
お使いの版で `tests/run_tests.py` と各スイープを実行してください。macOS では AppleScript の `do javascript` ブリッジが必要です。

トラブルシューティング：`docs/troubleshooting-com.md` · サイズ：`docs/sizes.md`

## ライセンス

MIT（`LICENSE` と `NOTICE` を参照）。Adobe のドキュメントやサードパーティのインデックスは再配布していません。API インデックスはお使いの Illustrator からローカルで生成されます。

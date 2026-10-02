# illustrator-com-skill

[English](README.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · **한국어**

코딩 에이전트(Claude Code 등)가 **Windows의 Adobe Illustrator**를 조작하게 해 주는 스킬입니다. 모든 기능은 샌드박스 문서에서 실제로 실행하고
**결과를 다시 읽어** 확인합니다(DOM 값, 내보낸 픽셀, Illustrator가 저장 파일에 실제로 기록한 효과 매개변수). 추측하지 않습니다.

[photoshop-com-skill](https://github.com/Moksa1123/photoshop-com-skill)과 같은 원칙으로 만들었습니다.

## 구성

| 부분 | 하는 일 |
|---|---|
| `lib/ai_run.py` | COM으로 ExtendScript를 실행하고 결과를 반환합니다. COM 형식 라이브러리가 등록되지 않아도(`TYPE_E_LIBNOTREGISTERED`) 동작하고 "스크립트를 실행할까요?" 창이 뜨지 않으며, **Illustrator의 모달 대화상자에 스스로 응답**합니다: 취소(기본값, 멈추지 않음), 확인, 또는 필드 입력(`["sel", "type:30", "tab", "ok"]`). 스크립트 엔진 오류도 감지해 복구합니다. |
| `lib/ailib.jsx` | 아트보드 왼쪽 위 기준 좌표를 쓰는 테스트된 디자인 라이브러리: 도형과 SVG 패스, RGB/CMYK/별색/그라디언트, 선 스타일, 혼합 스타일 텍스트, 패스 위 텍스트, 텍스트 맞춤, 문자/단락 스타일, 스타일을 유지하는 찾기·바꾸기, 패스파인더(합치기, 앞면 오브젝트 제외, 교차, 교차 영역 제외, 나누기, 동색 오브젝트 분리, 병합, 자르기, 윤곽선, 뒷면 오브젝트 제외), 정렬/분포/그리드, 클리핑, 컴파운드 패스, 심볼, 그래픽 스타일, 반복, 블렌드, 가져오기/포함/이미지 추적/래스터화, 색상 재지정, 안전 영역 안내선이 있는 새 문서, PNG/JPG/WebP/SVG/PDF/PSD/화면용 내보내기. |
| `presets/effects.json` | **효과 메뉴의 모든 효과를 대화상자 없는 `applyEffect` XML로**(그림자, 광선, 변형, 3D와 재질, Photoshop 필터…). 기본 매개변수와 형식은 Illustrator가 직접 저장한 파일에서 다시 읽은 것입니다. |
| `lib/fingerprint.jsx`, `tools/ai_dump.py` | 문서 지문(DOM 전체)과 비압축 `.ai` 리더. DOM에서 보이지 않는 것(모든 매개변수가 포함된 라이브 효과, Photoshop 필터의 바이너리 설명자, 안정적인 아트 해시)을 꺼냅니다. |
| `index/` | **사용자의 Illustrator에서 생성하는** API 인덱스(`ScriptingSupport.aip` 안의 형식 라이브러리 + 런타임 리플렉션), 단축키 세트에서 수집한 전체 메뉴 명령 목록, 조회 도구(`find`, `class`, `enum`, `member`, `menu`, `effect`, `stats`). |
| `tests/` | 라이브러리 테스트(`run_tests.py` → `REPORT.md`)와 모든 메뉴 명령·효과·도구 스윕(`menu_sweep.py`, `effects_sweep.py`, `tools_sweep.py`) → `CAPABILITIES.md`: 각 항목을 스크립트로 하는 방법과 검증 방법. |
| `presets/sizes.json` + `tools/sizes.py` | 54가지 디자인 크기(Instagram, Facebook, Open Graph, LINE, YouTube, TikTok, Google Ads, Amazon, Shopify, Etsy, Shopee, momo…), 안전 영역과 출처 포함. `new <id>`로 안내선이 있는 아트보드를 엽니다. |
| `tools/html2ai.py` | 고정 크기 HTML 레이아웃 → **편집 가능한 벡터** Illustrator 문서: 상자는 도형(칠, 선형 그라디언트, 테두리, 둥근 모서리, 그림자), 사진은 보이는 그대로 포함, 인라인 SVG는 패스, 텍스트는 실제 텍스트 프레임이 됩니다. |
| `tools/logo_package.py`, `tools/brand_assets.py` | 완성된 로고 키트(JSON 설정 하나)로 업계 표준 **로고 납품 패키지** 생성: RGB 벡터, 바로 인쇄할 수 있는 CMYK AI/EPS/PDF-X-1a(회색은 K 단색, 브랜드 잉크 K 값, 별색 판, 파일별 색상 점검), PNG 64–4096 px(300 ppi), SNS 아바타/커버/Open Graph/이메일, 파비콘과 앱 아이콘. 이어서 용도별로 정리된 폴더(인쇄/디지털/SNS/웹/명함/가이드라인/원본/상표)로 다시 배치합니다. |
| `tools/tipo_form.py`, `tools/md_docx.py` | 대만 지식재산국(TIPO) 상표 출원 보조: 상표 견본(JPG + TIF, 300 dpi, 7.6 cm), 공식 T0101 출원서 작성(체크 칸은 양식 자체의 칸에 표시), Markdown → Word를 통한 정식 DOCX/PDF(표 머리글 행을 페이지마다 반복, 행을 나누지 않음). |
| `tools/ui.py`, `tools/capture_commands.py`, `tools/make_graph_fixture.py` | 화면에만 있는 소수의 기능을 위한, Illustrator 창에만 한정된 화면/키보드 제어. |

## 검증 범위(Illustrator 2024 / 28.0)

<!-- coverage:start -->
- **메뉴 명령: 스크립트로 실행 가능한 디자인 명령 452/452 전부 검증(100.0%). Illustrator가 막는 2개를 포함하면 452/454(99.6%).** 나머지 181개는 UI/환경 설정/웹/생성형 AI 명령입니다(n/a, 명령마다 이유 기재). 모든 ✅는 샌드박스 문서에서 실행하고 결과를 다시 읽어 확인했습니다.
- **효과: 115/115**개의 효과 메뉴 효과를 LiveEffect XML로 대화상자 없이 적용하고, 모든 매개변수를 저장된 파일에서 다시 읽음(`presets/effects.json`).
- **라이브러리: 40/40**개 테스트 통과(`tests/REPORT.md`): DOM 재확인, 내보낸 픽셀, 내보낸 파일 디코딩, 저장 파일의 효과.
- **도구: 60/85**개 선택 후 재확인. 나머지는 `selectTool`은 받아들이지만 `getSelectedToolName()`이 예외를 던집니다(모두 스크립트 대안 있음).
- 차단됨(증거는 `tests/blocked.json`): File > Save Selected Slices; File > Print.

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

명령별 스크립트 실행 방법과 검증 방법: [tests/CAPABILITIES.md](tests/CAPABILITIES.md).
<!-- coverage:end -->

## 설치

Windows 10/11, Adobe Illustrator, Python 3.9+, Node 18+가 필요합니다.

```bash
npm install -g illustrator-com-skill
illustrator-com init --ai claude -g      # 또는: npx illustrator-com-skill init --ai claude -g
illustrator-com setup                    # pip install -r requirements.txt + 사용자의 Illustrator로 API 인덱스 생성 + doctor
```

`init`은 런타임(`lib/`, `tools/`, `index/`, `tests/`, `presets/`)을 `~/.illustrator-com-skill/`에 한 번만 복사하고,
각 어시스턴트에 그것을 가리키는 `SKILL.md`를 씁니다. 사용자의 Illustrator에서 만든 API 인덱스는 한 번만 만들면 모든 어시스턴트가 공유하며, 업데이트해도 사라지지 않습니다.

```bash
illustrator-com init                       # 어시스턴트를 대화형으로 선택
illustrator-com init --ai cursor,windsurf  # 현재 프로젝트에만(.cursor/skills/…, .windsurf/skills/…)
illustrator-com init --ai all -g           # 사용자 전역 skills 폴더가 있는 모든 어시스턴트
illustrator-com doctor --smoke             # Windows, Python, 패키지, Illustrator COM, 인덱스, 실제 스크립트 1개
illustrator-com list | info | versions | uninstall [--purge]
```

### 14개 AI 플랫폼

| `--ai` | 어시스턴트 | 프로젝트 | 전역(`-g`) |
|---|---|---|---|
| `claude` | Claude Code | `.claude/skills/illustrator-com/` | `~/.claude/skills/` |
| `cursor` | Cursor | `.cursor/skills/illustrator-com/` | `~/.cursor/skills/` |
| `windsurf` | Windsurf / Devin Desktop | `.windsurf/skills/illustrator-com/` | — |
| `antigravity` | Antigravity / 범용 에이전트 | `.agent/skills/illustrator-com/` | `~/.gemini/antigravity/global_skills/` |
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

어시스턴트는 Illustrator가 설치된 Windows 컴퓨터에서 실행되어야 합니다. 클라우드 에이전트(Claude.ai 웹, Copilot coding agent, Codex cloud)는 로컬 Illustrator에 접근할 수 없습니다.

### 업데이트

```bash
illustrator-com update                   # npm 최신 버전 → 런타임과 기록된 모든 설치
illustrator-com check                    # 새 버전이 있는지(결과는 24시간 캐시)
illustrator-com config auto-update on    # check가 새 버전을 찾으면 자동 설치
```

설치된 모든 `SKILL.md`는 세션을 시작할 때 `check --quiet`를 한 번 실행하도록 에이전트에게 안내하므로, 새 버전이 나오면 자연스럽게 알 수 있습니다.
자동 업데이트는 **기본적으로 꺼져** 있습니다. 켜지 않는 한 작업 도중에 버전이 바뀌지 않습니다. 업데이트해도 API 인덱스(`index/ai-dom.json`)는 유지되고,
수정한 런타임 파일은 `~/.illustrator-com-skill/_state/backup/`에 백업됩니다.

스킬 자체를 개발할 때: `node bin/illustrator-com.mjs init --link --ai claude -g`로 런타임을 복사하지 않고 체크아웃에 연결합니다.

## 빠른 시작

```bash
python lib/ai_run.py -e "app.version"
python tests/run_tests.py                  # 사용자의 Illustrator에서 되는 것 -> tests/REPORT.md
python index/build_index.py                # 사용자의 Illustrator로 API 인덱스 생성
python index/ai_api.py find gradient stop
python index/ai_api.py menu pathfinder     # 메뉴 명령과 검증 상태
python index/ai_api.py effect shadow       # 대화상자 없는 효과 XML
python tools/sizes.py new ig_story_reel    # 안전 영역 안내선이 있는 1080x1920 아트보드
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

## 원칙

- **추측하지 말고 검증한다.** "오류 없음"은 증거가 아닙니다. 선택과 같은 호출에서 실행한 메뉴 명령은 이전 선택에 작용하고, 많은 DOM 쓰기는 오류 없이 무시되며,
  열려 있는 대화상자는 모든 것을 막습니다. `CAPABILITIES.md`의 모든 행은 실행 후 다시 읽어 확인했습니다.
- **대화상자도 API의 일부.** 대화상자만 있는 명령은 대화상자를 통해 조작합니다(입력 후 확인). 키 입력은 Illustrator의 대화상자 창에만 전달됩니다.
- **생성형 AI 기능은 쓰지 않습니다**(생성형 색상 재지정, 텍스트로 패턴, 목업 베타) — Photoshop 스킬과 같은 방침입니다.
- **크기 규격은 바뀝니다.** 각 프리셋에는 출처와 확인 날짜가 있습니다. 큰 캠페인 전에 다시 확인하세요.

## 요구 사항

Windows 10/11, Python 3.9+, Node 18+(설치 프로그램만). Illustrator 2024(28.0)에서 개발·검증했습니다. 다른 버전도 같은 COM 인터페이스로 동작할 것으로 보이지만 검증되지 않았으므로,
사용 중인 버전에서 `tests/run_tests.py`와 각 스윕을 실행하세요. macOS에서는 AppleScript `do javascript` 브리지가 필요합니다.

문제 해결: `docs/troubleshooting-com.md` · 크기: `docs/sizes.md`

## 라이선스

MIT(`LICENSE`와 `NOTICE` 참고). Adobe 문서나 서드파티 인덱스는 재배포하지 않습니다. API 인덱스는 사용자의 Illustrator에서 로컬로 생성됩니다.

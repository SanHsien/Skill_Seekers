# 維護決策

## 2026-09-12：建立 Windows-first 維護型 fork

**決定**：fork `yusufkaraaslan/Skill_Seekers`，保留 MIT License 與完整歷史。本線預設分支用 `main`。本線聚焦繁中文件、Windows 開發 gate、Windows CI，以及逐筆審查的上游追蹤。

**理由**：`Skill_Seekers` 是一套強大的開源 AI Agent 技能與知識庫轉換層，支援 18 種常見數據來源輸入、40 個 MCP 工具、以及自動打包至 22 個平台。本 fork 補足 Windows 11 原生開發與驗收骨架、繁體中文維護入口，以及可審計的上游追蹤機制。

**限制**：

- 不把 fork 包裝成原創專案，不移除原作者 Yusuf Karaaslan 與官方連結。
- 不發佈 PyPI 取代官方管道。
- 維護 gate 不預設安裝重型套件。
- 上游更新必須逐筆審查。

## 2026-09-12：依賴新鮮度追蹤

**決定**：`tools/check_dependency_freshness.py` 納管 `requirements-dev.txt` 與 `requirements.txt`。

**理由**：維護依賴（`pytest`, `ruff`）與產品依賴獨立分開，透過新鮮度檢查機制持續監控版本演進。

## 2026-09-12：上游檢查涵蓋 Commit、PR 與 Issue 三面向

**決定**：`check_upstream_updates.py` 以 `--state all` 收集上游 PR 與 Issue，並追蹤 Commit SHA。`gh` 失敗時 fail closed（exit 2）。

**理由**：未合併即關閉的 PR 與待處理的 Issue 同樣可能揭露重要缺陷或需求。排程報告必須確保「未檢查」與「沒有新變更」截然分明。

## 2026-09-12：日常直接推 main

**決定**：日常維護修改在本機跑 `tools\dev_check.ps1` 後直接推 `origin/main`。Dependabot 與外部貢獻仍走 PR，合併前讀 diff。

**理由**：對齊 SanHsien 體系其他維護 fork 的治理規範。

## 2026-09-12：上游分支、PR 與 Issue 首次盤點結論

**決定**：
1. **上游分支**：上游存在 `development`（日常開發）與 `main`（穩定發佈）等分支。本 fork 以穩定版本 `upstream/main`（release v3.9.1，`c333a37`）為起始基線。
2. **上游 PR（水位 #468）**：
   - 最新 PR `#468`（feat: support MiniMax video input and thinking modes）、`#465`（fix(enhance): accept --enhance-level on skill-seekers-enhance）、`#464`（fix(security): validate Git config cache names）、`#463`（feat(index): add opt-in SQLite skill search）等處於 open 狀態，待上游合併並發布下一版本時再行取用。
3. **上游 Issue（水位 #469）**：
   - 水位記錄為 `#469`，後續新 issue 將由每週排程工具自動納入審查報告。

## 2026-09-13：上游 PR、Issue 深度審查與 Bug 修復、Tag/分支清理

**決定**：
1. **Tag 清理**：原倉庫包含 36 個 release tag（`v0.3.0` ~ `v3.9.1`）。依據指令「只保留最新 tag」，本機與 GitHub 遠端（`SanHsien/Skill_Seekers`）刪除所有舊 tag，僅保留最新版 `v3.9.1`。
2. **分支清理**：刪除本 fork 遠端殘留的 26 個非預設分支（`development`、`feature/*`、`fix/*`、`claude/*` 等），`SanHsien/Skill_Seekers` 僅保留單一主分支 `main`。
3. **PR #465 修復引進**：在 `src/skill_seekers/cli/arguments/enhance.py` 補齊 `--enhance-level` 選項（choices: [0, 1, 2, 3]），並在 `src/skill_seekers/cli/enhance_command.py` 實作 level 0 跳過邏輯與接收 list 參數。此修復解決 `doc_scraper.py` 與 `video_scraper.py` 轉發該參數時導致的 `unrecognized arguments: --enhance-level` 崩潰問題。
4. **PR #456 修復引進**：在 `src/skill_seekers/cli/doctor.py` 補上 `main(args=None) -> int` 函式，使 `pyproject.toml` 中的 `skill-seekers-doctor = "skill_seekers.cli.doctor:main"` console script 可以正常啟動，不再觸發 `ImportError`。
5. **PR #464 / Issue #462 安全修復引進**：在 `src/skill_seekers/services/git_repo.py` 實作 `validate_path_segment()` 嚴格校驗函數，阻擋 `..`、斜線、反斜線及 Windows 磁碟機代號等路徑穿越攻擊（CWE-22），防止惡意 `source_name` 或 `config_name` 逃逸快取根目錄造成任意檔案刪除或覆寫。同步於 `src/skill_seekers/mcp/tools/source_tools.py` 與 `server_legacy.py` 套用防護。並對 `import git` 提供安全 fallback，確保輕量維護環境可獨立運作。
6. **CLI 套件容錯引進（R-12）**：`src/skill_seekers/cli/__init__.py` 對 `requests` 與 `pydantic` 等重型依賴增加 `try...except ImportError` 保護，避免 `skill-seekers-doctor` 診斷工具或輕量測試環境在未安裝產品依賴時直接崩潰。
7. **上游 PR 與 Issue 水位鎖定**：
   - 經審查目前 upstream 10 個 open PR（#450, #454, #456, #457, #458, #459, #463, #464, #465, #468）及 25 個 open Issue（#462, #469 等），暫不引進非核心之第三方支付/贊助插件（#469）或草稿型大型改動（#468）。
   - 水位記錄為 PR `#468`、Issue `#469`，後續由每週排程工具持續監控。


## 2026-09-29：chromadb、nltk 安全警示暫不處理

**決定**：5 個 open Dependabot alerts（`chromadb` critical 2、high 2；`nltk` high 1）目前無修補版，
`uv.lock` 已是 PyPI 最新版（chromadb 1.5.9、nltk 3.10.3）。警示保持 open，不 dismiss，好讓修補版
釋出時 Dependabot 自動開 PR。

**理由**：

- chromadb 的四個漏洞都在 ChromaDB HTTP 伺服器（`/api/v2` 端點、多租戶授權）。本專案只當用戶端：
  `cli/adaptors/chroma.py` 用 `PersistentClient`（同程序、不開埠）或 `HttpClient` 連使用者自己跑的伺服器，
  `mcp/tools/vector_db_tools.py` 的 `chromadb.Client()` 只是輸出給使用者的範例文字。自己跑 `chroma run` 時不要綁到對外介面。
- nltk 由 `llama-index` 間接帶入，`src/` 未直接使用 nltk，也不把外部路徑傳給它的模型檔 API。

**觸發條件**：chromadb 或 nltk 發布修補版、或本專案開始自己啟動 ChromaDB 伺服器時重評。


## 2026-09-30：上游 PR #470–#474 審查（無新 main commit）

**決策**：上游 `main` 無新 commit（水位維持 `c333a37`）；PR #470–#473 已合併至上游 `development`，#474 為開放中。chromadb／nltk 的安全暫不處理決定（2026-09-29）不變。

| 項目 | 結論 | 理由 |
| --- | --- | --- |
| #470、#472 | 不適用 | 贊助商版位（README 12 語系）增刪，本 fork 不維護 |
| #471 | 暫緩 | 單檔測試修正（benchmark compare 改為確定性）；隨上游 main 釋出時抵達，非行為缺陷 |
| #473 | adoption pending：本機無法驗證 | 修正 `--enhance-level` 未採用設定檔預設值（9 檔 +135/-11）。`cherry-pick -x c413bc3` 僅 CHANGELOG 衝突，但本機 dev_check 不執行產品測試（未安裝產品依賴，`tests/test_execution_context.py` 無法執行），且本 fork 已自行修改 `enhance.py`（PR #465）。觸發條件：上游釋出至 main 後隨 commit 軸審查，或維護者安裝產品依賴後可驗證時 |
| #474 | 暫緩 | 開放中，新增 Requesty adaptor（36 檔），屬新功能，尚未合併 |

**基準線**：`tools/upstream_baseline.json` PR 水位推進至 474、issue 水位維持 469、日期 2026-09-30。Baseline 代表已審查，未代表已合併。


## 2026-10-24：Dependabot 警示重盤（105 筆 open）與修補

**決定**：open 警示由 2026-10-01 的 5 筆增為 105 筆（critical 12、high 54、medium 36、low 3）。警示筆數是以 `uv.lock` 與 `requirements.txt` 兩份清單分開計算，同一個 advisory 在兩份清單各算一筆。依艦隊規則，有修補版的 critical／high 一律修；本輪順手把同一批有修補版的 medium／low 也一起清掉。全部在分支 `security/deps-20261024` 以單一 PR（#13）處理，不 merge、不 dismiss 任何警示。每個套件獨立一個 commit，以 `uv lock --upgrade-package <套件>==<最小修補版>` 重新產生 `uv.lock`，每次都檢查 lock diff：來源仍只有 PyPI。

| 套件 | 舊版 → 新版 | 清掉的警示（advisory 數；警示筆數） | 備註 |
| --- | --- | --- | --- |
| certifi | 2025.11.12 → 2026.10.19（`requirements.txt` 2025.10.5 → 2026.10.19） | critical 1；2 筆 | 最小修補版 |
| fsspec | 2026.2.0 → 2026.6.0 | high 1；1 筆 | 最小修補版 |
| Pillow | 12.3.0 → 13.0.0（僅 Python >= 3.11） | 共 39 個 advisory：critical 4、high 23、medium 12；78 筆 | `uv.lock` 與 `requirements.txt` 都以 `python_version` 條件拆開，見下方 Python 3.10 暫緩 |
| nltk | 3.10.3 → 3.10.4 | high 1；1 筆 | 見下方 |
| aiohttp | 3.14.3 → 3.14.4 | high 3、medium 3、low 2；8 筆 | 連帶 yarl 1.22.0 → 1.25.1（與 Dependabot PR #9 相同） |
| GitPython | 3.1.62 → 3.2.1 | high 1；1 筆 | |
| opentelemetry-api | 1.39.1 → 1.45.1 | medium 1；1 筆 | 連帶 opentelemetry 家族同步升級，並新增 `opentelemetry-exporter-otlp-common`（OpenTelemetry 官方套件，由 exporter 1.45.1 依賴；與 Dependabot PR #11 的鎖檔變更相同） |
| pypdf | 6.19.0 → 6.21.1 | medium 7、low 1；8 筆 | 最小修補版為 6.21.1（最後一個 low 警示的修補版） |
| multidict | 6.7.1 → 6.9.1 | medium 1；1 筆 | 最小修補版 |

本分支的 aiohttp、GitPython、opentelemetry-api、pypdf 與 Dependabot 的 PR #9、#10、#11、#12 是同樣的升級；這四個 PR 刻意不關閉也不合併，本分支合併後 Dependabot 會自行關閉。

**nltk**：2026-09-29 記錄為無修補版。現在 PyPI 有 3.10.4（2026-10-20 發布，變更說明為把模型存取、下載與外部程式路徑全數導入沙箱），而該警示的受影響範圍是 `<= 3.10.3`，3.10.4 已在範圍外，故升級；警示的 `first_patched_version` 仍是空值，是否關閉由 GitHub 重掃決定。這個升級獨立成一個 commit，若發現 llama-index 路徑受影響可單獨還原。

**暫緩（沒有可驗證的修補版）**：

- **Pillow 在 Python 3.10**：
  - 現況：`uv.lock` 與 `requirements.txt` 的 `python_version < "3.11"` 分支仍是 Pillow 12.3.0。這一支對應的 Pillow 警示（`uv.lock` 與 `requirements.txt` 都有）會持續 open，不 dismiss。
  - 理由：修補版 13.0.0 的 `requires_python` 為 `>=3.11`（PyPI 中繼資料）；`pyproject.toml` 宣告 `requires-python >=3.10`，CI 矩陣也實際測 3.10，所以 3.10 沒有可安裝的修補版。放棄 3.10 是產品決策，不在依賴升級範圍，故不改 `requires-python`。
  - 觸發條件：停止支援 Python 3.10（屆時把 `requires-python` 改為 `>=3.11` 並重新產生鎖檔、移除 3.10 分支），或 Pillow 發布支援 3.10 的修補版時重評。
- **chromadb 1.5.9**（critical 2、high 2，皆為 `uv.lock`）：PyPI 最新版仍是 1.5.9，與 2026-09-29 相同，警示 `first_patched_version` 皆為空。理由與限制條件沿用 2026-09-29 的決定（本專案只當用戶端，漏洞在 ChromaDB HTTP 伺服器）。觸發條件不變：chromadb 發布 > 1.5.9 的版本、或本專案開始自己啟動 ChromaDB 伺服器時重評。

**合併後預計剩餘的警示**：chromadb 4 筆（無修補版）與 Pillow 的 Python 3.10 分支（鎖檔仍含 12.3.0，兩份清單的警示可能維持 open）；其餘由 GitHub 在合併後重掃關閉。nltk 是否關閉取決於重掃。

**驗證**：`uv lock --check` 通過；`tools\dev_check.ps1` 全綠（56 passed、1 skipped）；以 `uv sync --locked`（Python 3.12）安裝後，跑上游 fast 測試指令（`pytest tests/ -n 6 --dist=loadfile -m "not slow and not integration and not e2e and not network and not serial and not mcp_only"`），修補前後各 75 個失敗，失敗集合完全相同（皆為本修補前就存在的失敗，與依賴升級無關）；本 fork 的 CI 不執行這套產品測試。Pillow 升級的 commit 訊息寫「50 GHSA alerts」不精確，正確數字為 39 個 advisory、78 筆警示（見上表）。

## 2026-10-24（續）：PR #13 後新增的 pypdf、setuptools 警示

PR #13 合併後出現 4 筆新警示（皆為 `uv.lock`）：pypdf high 3 筆（#378–#380，受影響範圍 `< 6.21.2`）、setuptools low 1 筆（#381，受影響範圍 `>= 38.2.2, < 84.1.0`）。

| 套件 | 版本 | 備註 |
|------|------|------|
| pypdf | 6.21.1 → 6.21.2 | 最小修補版 |
| setuptools | 84.0.0 → 84.1.0 | 最小修補版 |

以 `uv lock --upgrade-package <套件>==<版本>` 逐一升級，鎖檔差異只有這兩個套件、來源皆為 PyPI；`requirements.txt` 沒有這兩個套件的 pin，不需修改。Dependabot PR #9–#11 已被 #13 取代，不處理。Pillow（Python 3.10 分支）與 chromadb 的暫緩決定不變。


## 2026-10-24（續）：採用上游 main 至 v3.10.0（`d26c2e3`）

**決策**：整批採用上游 `main` 自 `c333a37` 起的 74 個 commit（244 個檔案，含 Seeker HUD 網頁介面、`doctor --json`、`quality --json`、`detect` 指令、SQLite 技能索引、`path_safety`、Git 設定快取名稱驗證、`--enhance-level` 預設值修正、MiniMax 影片輸入、PDF 向量圖擷取）。含上游 PR #454、#456–#459、#463、#464、#468、#471、#473 的內容；#470、#472 是贊助商版位。本 fork 的產品碼與起點相比只有 26 個檔案的差異，其中的 `git_repo` 路徑驗證（PR #8 之前的修正）上游已用 `services/path_safety.py` 重做同一件事，採用上游版本。

**做法**：fork 歷史是壓縮過的，與上游沒有共同祖先，不能 `merge`。改用 `git diff c333a37 upstream/main` 以 `git apply --3way` 套用，排除 `CLAUDE.md`（本 fork 已刪除）。8 個衝突檔的處理：

| 檔案 | 處理 |
| --- | --- |
| `README.md`、`AGENTS.md`、`CONTRIBUTING.md` | 保留本 fork 精簡版（上游版為產品完整說明） |
| `uv.lock` | 保留本 fork 版（含 2026-10-24 的安全升級），再 `uv lock` 只更新 `skill-seekers` 自身版本 3.9.1 → 3.10.0 |
| `.gitignore` | 兩邊都保留 |
| `doctor.py`、`server_legacy.py`、`source_tools.py` | 採用上游（`doctor.main` 改為由 `DoctorParser` 建立參數、`validate_path_segment` 改由 `path_safety` 匯入） |

套用後額外調整三處：`services/git_repo.py` 採用上游並保留本 fork 的 `git` 選用匯入（`tools/tests` 在沒有產品依賴的 CI 環境要能匯入）；`tools/tests/test_fixes.py` 的 `doctor_main` 測試改為 monkeypatch `sys.argv`（上游 `main(args)` 的參數是已解析的 Namespace）；`README.en.md` 的贊助商區塊改成與上游 `README.md` 一致（Atlas Cloud 版位及圖片已被上游 #470 移除，連結檢查會失敗）。

**驗證**：
- `pwsh tools\dev_check.ps1` 全綠；`uv lock --check` 通過；`skill-seekers --version` 為 3.10.0，`skill-seekers-doctor --json` 輸出合法 JSON。
- 上游 fast 測試指令（`uv sync --locked --python 3.12 --all-extras`）：基準 `origin/main` 81 失敗，採用後 101 失敗 + 1 error；以測試 ID 比對，只在採用後失敗的有 37 項、只在基準失敗的有 16 項。新增的 37 項主要分布在 `test_web_*`（上游新測試，Windows 不相容：POSIX 權限位元、符號連結、路徑分隔符、檔案鎖、`bootstrap_skill.sh`）、`test_bootstrap_skill`、`test_skill_indexer`（`PermissionError`／WinError 32）、`test_create_integration_basic`（`skills\godot` 對 `skills/godot`）；`test_cli_paths` 兩項單獨重跑通過（負載造成逾時）。未發現既有行為的回歸。基準中有 16 項採用後反而通過（含 `test_create_integration_basic`、`test_cli_refactor_e2e`、`test_minimax_multimodal`、`test_issue_219_e2e`，部分應是上游修正帶來，部分可能與負載有關，未逐項區分）。本 fork 的 CI 不跑產品測試套件，上游新增的 `frontend`（HUD 瀏覽器測試）工作也加上與其他上游工作相同的 `github.repository` 守衛，不在 fork 執行。

**PR／issue 軸**：上游 #475（zh-CN README 措辭）、#476（MCP 可選參數接受 null）、#477（MiniMax 預設改 M3.1 Flash）都還是 open、未合併，暫緩，水位推到 477；觸發條件是它們合併進上游 `main`，之後隨 commit 軸審查。issue 軸無新項目（水位 469）。

**未做**：未修 Windows 上的上游測試（會與上游持續分歧）；#473 的 `enhance.py` 衝突預測已不存在（由 commit 軸整批帶入）。基準線 `reviewed_through` 推進到 `d26c2e3e0384c664a6fcc71ca10ddcd26026ac0b`。


## 2026-10-24（續）：採用上游 v3.10.0 後新增的 34 筆 CodeQL 警示

**背景**：`b435118` 推上 main 後，CodeQL 新開 34 筆（高風險 25：path-injection 23、clear-text-logging 1、polynomial-redos 1；中風險 9：stack-trace-exposure 7、log-injection 2），全部在上游 v3.10.0 帶進來的程式碼（`web/`、`cli/enhancement_workflow.py`、`cli/config_manager.py`）。上游 `development`（`5b5d8df`）沒有對應修正，故自行處理。

**HUD 的威脅模型**：Seeker HUD 只綁 `127.0.0.1`，`app.py` 的中介層拒絕非 localhost 的 Host 與非 `localhost:3000`／`127.0.0.1:3000` 的 Origin，行程以本機使用者身分執行。「專案路徑」「分析目錄」「設定檔路徑」本來就是讓本機使用者指定任意本機路徑，所以這類輸入不是跨權限邊界。下列修補只處理「有明確邊界可守」或「只是資料流被誤判」的位置。

| 警示 | 位置 | 判斷與處理 |
| --- | --- | --- |
| clear-text-logging #67 | `config_manager.py` 308 | 誤判：印出的是 provider 名稱，不是金鑰。改為由常數表取顯示名稱，不再讓 provider 參數進入輸出 |
| log-injection #69、#70 | `enhancement_workflow.py` | 真問題（使用者提供的 workflow 名稱／路徑寫進日誌可含換行）。新增 `_log_safe()` 去除 CR／LF，改用 `%s` 參數化 |
| polynomial-redos #68 | `analyze.py` `REPO_RE` | 改為 `[A-Za-z0-9_.-]{1,100}/[A-Za-z0-9_.-]{1,100}`（GitHub 名稱上限 100、ASCII），長度有界 |
| stack-trace-exposure #60–#66 | `configs.py`、`skill_detail.py`、`workflows.py`、`enhance_status.py` | 回應不再帶例外內文：驗證器當機、YAML 語法錯誤（只回行號）、workflow 載入失敗、狀態檔讀取失敗都改成固定訊息＋例外類別名，完整例外只寫日誌 |
| path-injection（有邊界） | `app.py` 的 SPA 靜態檔、官方設定下載目的地、市集安裝目的地；`registry.py` 的還原封存；`workflows.py` 的複製／儲存／刪除 | 改用新增的 `paths.contained(base, *parts)`（`normpath` 後必須在 `base` 內，否則 `ValueError`）；SPA 路由改以 `realpath`＋`startswith` 檢查 |
| path-injection（本機使用者指定的路徑） | `app.py`（新增專案、`/api/library/build` 的 `config_path`）、`analyze.py`、`configs.py`（`generate` 的目錄）、`enhancement_workflow.py`（`--workflow` 路徑，CLI 本來就接受任意路徑） | 不改：這些參數的用途就是指定任意本機路徑，限制會破壞功能；來源是本機使用者而非遠端。不 dismiss，保持 open，待維護者決定是否以「won't fix」關閉 |
| path-injection（匯集點） | `paths.py` 的 `atomic_write` | 這是 sink，污點來自上述呼叫端；呼叫端改完後以重掃結果為準 |

**驗證**：`tests/test_web_*.py` 失敗集合是修補前的子集（修補前 29 項、修補後 25 項，沒有新增失敗；差異來自本次以隔離 `HOME` 執行，不讀本機真實技能目錄）；`test_config_manager`、`test_workflows_command`、`test_workflow_*`、`test_mcp_workflow_tools` 共 155 項全過；新增 `tests/test_codeql_hardening.py` 7 項；`dev_check.ps1` 綠。重掃後的實際結果記在下一則。

**重掃結果（`e2aea07`）**：34 筆降為 15 筆。clear-text-logging、polynomial-redos、stack-trace-exposure（7）全數關閉，path-injection 23 降為 13。剩下的 log-injection 2 筆（`_log_safe` 的寫法 CodeQL 認不得）與 SPA 路由的 path-injection 2 筆（`realpath`＋`startswith` 不被辨識）在下一個 commit 改成它認得的寫法（`replace("\r", "").replace("\n", "")`、`normpath`＋`startswith` 後再以 `realpath` 複查符號連結）。其餘 11 筆 path-injection 屬上表「本機使用者指定的路徑」，刻意不改、不 dismiss。

**最終重掃（`30cc516`，CodeQL run 成功）**：34 筆降為 13 筆，全是 path-injection。log-injection、clear-text-logging、polynomial-redos、stack-trace-exposure 全數關閉。剩下的 13 筆：

- 11 筆是本機使用者指定的路徑，刻意不改：`app.py` 845（新增專案）、1195／1196／1199（`/api/library/build` 的 `config_path`）、1307（市集安裝，`item_path` 已限定在快取清單內）；`analyze.py` 51、`configs.py` 134（分析／產生設定的目錄）；`enhancement_workflow.py` 131／135／137／162（`--workflow` 接受任意路徑的 CLI 功能）。
- 2 筆是 SPA 靜態檔路由（`app.py` 1454／1455）：程式已用 `normpath`＋`startswith` 限制在 `dist` 內，並以 `realpath` 複查符號連結；審查者在 Windows 以真實目錄連接點（`mklink /J`）實測：`../` 穿越、絕對路徑、UNC、兄弟目錄前綴（`Dist2`）、經連接點逃出 `dist` 全部回 404。CodeQL 不認得這個檢查形式（試過 `realpath`＋`startswith`、`normpath`＋`startswith` 兩種），判為誤判。

這 13 筆都不 dismiss，保持 open，是否以「won't fix／false positive」關閉由維護者決定。

## 2026-10-25：把「本機使用者指定路徑」的 API 端點改成真檢查

**背景**：上一則把剩下 13 筆 path-injection 中的 11 筆歸為「本機使用者指定路徑」。維護主管要求：只要有任何 server／API 端點會傳進來就必須修，不能直接關。逐筆確認後，其中 7 筆確實是 HTTP 端點的請求內容（HUD 只綁 127.0.0.1 並限制 Host／Origin，但本機其他行程仍可呼叫），1 筆（`--enhance-workflow`）可由 HUD 的建立工作旗標傳入 CLI 載入器。

| 位置 | 處理 |
| --- | --- |
| `app.py` `POST /api/projects`、`POST /api/library/build`；`analyze.py` `POST /api/analyze`（dir）；`configs.py` `POST /api/configs/generate`（dir） | 新增 `paths.user_path(root, value)`：相對路徑以工作區為基準、展開 `~`，`normpath` 後必須落在「工作區」「設定的 output／configs 目錄」「設定來源快取目錄」「使用者家目錄」或 `SKILL_SEEKERS_ALLOWED_ROOTS`（`os.pathsep` 分隔，可寫磁碟機根目錄如 `D:\`）之下，否則 `ValueError`（全域處理成 400，訊息會提示該環境變數）。檢查只比對正規化後的字串，不追連結；呼叫端之後仍會 `resolve()`，家目錄內指向他處的連結仍可通過。**行為變化（影響範圍比「系統目錄」大）**：凡不在上述範圍內的位置都會回 400，包含 `C:\GitHub\...`、`D:\...` 這類 Windows 常見的專案位置，需要用 `SKILL_SEEKERS_ALLOWED_ROOTS` 放行（已寫入 `docs/guides/WEB_UI.md`）；`/api/library/build` 指向允許範圍外的不存在檔案由 404 變 400（測試已更新並新增一項） |
| `app.py` `POST /api/marketplaces/install` | 不再對請求路徑做檔案系統操作：以字串 `normcase(normpath())` 與快取清單比對，命中後改用清單內的可信路徑。與舊版的差異：請求若給相對路徑或符號連結別名，舊版會先 `resolve()` 再比對，新版不會，會回 404（前端送的是清單上的 `path`，不受影響） |
| `web/runner.py` `_create_flag_argv` | `flags["workflows"]` 每一項必須通過 `safe_name`（與儲存使用者 workflow 時的規則相同，只接受單一名稱，不接受路徑；不合格會在工作執行時失敗，而不是在提交時回 400） |
| `enhancement_workflow.py`（`--workflow` 載入器） | 經上一項後，HUD 只能傳入名稱；剩下的只有執行者自己在命令列或 `workflows` 子指令給的路徑，屬 CLI 本來就接受任意路徑的功能。重掃後以 `won't fix` 關閉並附 `檔案:行號` |
| SPA 靜態檔路由 | 已限制在 `dist` 內並複查符號連結（審查者以 `mklink /J` 實測穿越、絕對路徑、UNC、兄弟目錄前綴、連接點逃逸皆 404）。重掃後以 `false positive` 關閉 |

**重掃與處置（`0f44a45`，CodeQL run 成功）**：改為 `user_path` 後，CodeQL 仍回報 16 筆 path-injection（污點仍經 `user_path` 流向 `Path`／檔案操作，它不把這個函式當作守衛），2026-10-25 逐筆 dismiss，每筆都附理由與 `檔案:行號`，目前 open 為 0：

- 4 筆 `won't fix`（#49–#52，`cli/enhancement_workflow.py` 131／135／137／162）：CLI `--workflow` 路徑來自執行者自己的參數；HUD 已不能傳路徑（`web/runner.py` 以 `safe_name` 限制）。
- 10 筆 `false positive`（#41、#42、#76–#83，`web/app.py` 846／847／1196／1197／1200、`web/registry.py` 592、`web/routes/analyze.py` 52／53、`web/routes/configs.py` 134 ×2）：API 路徑已由 `paths.user_path` 限制，超出範圍回 400，測試在 `tests/test_codeql_hardening.py`。
- 2 筆 `false positive`（#71、#47，`web/app.py` 1461／1462，SPA 路由）：見前一段的實測。

重新開啟條件：`user_path` 的允許範圍放寬，或有新的端點直接把請求內容傳給檔案操作。

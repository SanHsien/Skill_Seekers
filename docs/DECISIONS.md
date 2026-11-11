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


## 2026-10-25：上游 v3.10.0 帶進來的 `ui/`（npm）警示與 Dependabot PR #17–#21

**背景**：採用上游 v3.10.0 後多了 `ui/`（Seeker HUD 的 React 前端），Dependabot 針對 `ui/package-lock.json` 新開 41 筆警示與 5 個 PR（#17 source-map-js、#18 postcss-selector-parser＋tailwindcss、#19 zod、#20 brace-expansion、#21 vite）。這 5 個 PR 只改 `ui/package-lock.json`，其中 #18、#19、#21 另改 `ui/package.json`。

**做法**：不逐一合併（五個都改同一份鎖檔，分開合併會互相衝突），在 `ui/` 執行一次 `npm audit fix`（不加 `--force`），再把 `package.json` 的版本下限抬到修補版：`zod ^4.6.7`、`vite ^7.3.7`、`react-router ^7.18.2`。鎖檔結果：vite 7.3.7、zod 4.6.7、react-router 7.18.4、lodash 4.18.1（recharts 的傳遞依賴）、source-map-js、brace-expansion 等皆升到修補版；`npm audit` 從 19 個降為 3 個（中風險）。#17、#19、#20、#21 的內容都被涵蓋，推上 main 後 Dependabot 會自動關閉。

**驗證**：`npm ci`、`npm run lint`、`npm run build` 通過；`npm test`（Playwright，28 項）全過。本 fork 的 CI 不跑 `ui/`（上游的 `frontend` 工作已加 repository 守衛），所以證據是本機執行。

**zod 執行期**：`ui/src` 沒有任何檔案 `import` zod，建置後的 `web/dist/assets/*.js` 也不含 zod 程式碼；zod 只是 `ui/package.json` 的直接依賴，鎖檔已升到 4.6.7，但 HUD 的執行期沒有載入它，所以沒有執行期行為變化。

**延後（附證據）**：剩下 3 筆中風險（postcss-selector-parser `< 7.1.6`，經 `tailwindcss 3.4.19` → `postcss-nested` 帶入，皆為開發期建置工具）。唯一修法是 Dependabot #18 的 `tailwindcss 3 → 4`，我在暫存分支實測：安裝 `tailwindcss@4.3.3` 後 `npm run build` 失敗（`tailwindcss` 不能再直接當 PostCSS 外掛，需改用 `@tailwindcss/postcss` 並改寫 `postcss.config.js`、`tailwind.config.js`），所以 #18 不能直接合併，已關閉。Dependabot 不接受在多套件 PR 上用 `ignore this major version`，關閉只會略過這次版本，下次 `tailwindcss` 或 `postcss-selector-parser` 發佈新版時會再開 PR；刻意不用 `ignore these dependencies`，以免擋掉 `postcss-selector-parser` 6.x 的修補版。弱點是「選擇器解析的二次方複雜度」，輸入是本專案自己的 CSS，不接收外部輸入。觸發條件：上游把 HUD 遷移到 Tailwind 4，或 `postcss-selector-parser` 6.x 發佈修補版。


## 2026-10-25：放棄 Python 3.10 支援（最低版本 3.11）（已被「2026-11-04（續）：恢復 Python 3.10 支援，跟隨上游」取代）

**背景**：Python 3.10 本月底 EOL。Pillow 13.0.0 需 Python ≥3.11，而 3.10 分支只能停在 12.3.0，這讓 Dependabot 對 `uv.lock` 與 `requirements.txt` 各開 41 個 Pillow 警示（共 82 個）無法關掉。維護者決定放棄 3.10。

**與上游的差異**：上游 `main`（`d26c2e3`）與 `development` 仍宣告 `requires-python = ">=3.10"` 且 CI 測 3.10，無法對齊；本 fork 這項刻意與上游分歧。之後採用上游 commit 時，這些檔案的 3.10 相關行會衝突，一律保留本 fork 的 3.11：`pyproject.toml`（`requires-python`、classifier、`tomli` 條件依賴、ruff `target-version`、mypy）、`mypy.ini`、`uv.lock`、`requirements.txt`、上游的 `.github/workflows/{ci,release,tests,test-vector-dbs}.yml`、`tools/dev_check.ps1`、`render.yaml`。

**做法**：
- `requires-python >=3.11`；刪 3.10 classifier 與 `tomli; python_version < '3.11'`；`_version.py` 直接用 `tomllib`；`doctor` 的版本檢查改 3.11。
- `uv lock`（不升級）：只收斂原本分 3.10／3.11+ 兩支的版本，Pillow 只剩 13.0.0（networkx、numpy、onnxruntime、scikit-learn、scipy 同樣只剩 3.11+ 那一支），另移除 8 個僅 3.10 需要的套件（exceptiongroup、async-timeout、backports-asyncio-runner、importlib-metadata、zipp、coloredlogs、humanfriendly、pyreadline3），沒有任何套件升版。`requirements.txt` 的 Pillow 條件式合併為 `Pillow==13.0.0`。
- CI 矩陣移除 3.10（`ci.yml` 現為 3.11–3.14；上游工作 `tests.yml`、`test-vector-dbs.yml`、`release.yml` 也同步，這些在 fork 被守衛略過）。Docker 基底原本就是 3.12，不變；`render.yaml` 的 `PYTHON_VERSION` 由 3.10 改 3.12。
- ruff `target-version` 與 mypy 改 3.11：套用 `UP017`（`datetime.UTC`）、`UP015`、`UP041` 的安全自動修正，並清掉因此多出的未使用 import；`UP042`（`str` + `Enum` 改 `StrEnum`，會改變 `str()` 與格式化行為）列入忽略。
- 文件：README 各語言、`docs/`、安裝與設定腳本的「Python 3.10+」改 3.11+；歷史紀錄（CHANGELOG、DECISIONS 舊條目、REVIEW）不改。

**驗證**：`tools\dev_check.ps1` 綠；`ruff check src tests` 全過；上游 fast 測試指令（`uv sync --locked --python 3.12 --all-extras`）109 失敗 + 1 error，把這 110 項在改前的 `origin/main` 重跑，失敗集合完全相同（無新增失敗；失敗是 10-24 條目記下的 Windows 不相容）。

**警示重掃**：推送 `7393009` 後，main 的 CI、CodeQL、Dependency freshness 全綠；Dependabot open 由 87 降為 5（Pillow 82 全部關閉），剩 chromadb 4（無修補版，最新 1.5.9）與 postcss-selector-parser 1（開發期工具，等上游遷到 Tailwind 4），都是先前已記錄的延後；code scanning open 0。

**需注意**：main 的 branch protection 把 `test (windows / py3.10)` 列為必要檢查；這個檢查不會再出現。直接推 main 不受影響（`enforce_admins` 關閉），但之後要合併 PR（含 Dependabot）時該檢查會一直 pending。這需要維護者在 GitHub 設定移除該必要檢查，本次未改 branch protection。


## 2026-10-28：embedding 伺服器的 path-injection 警示 #84／#85 與 chromadb 警示 #115／#222–#224

**背景**：CodeQL #84、#85（`py/path-injection`，`embedding/server.py` 的 `embed_skill`，皆在 `Path.exists()` 那一行）自 2026-10-26 起 open。該伺服器預設綁 `0.0.0.0`（`EMBEDDING_HOST`）、沒有驗證，CORS 來源可由 `CORS_ORIGINS` 設定，所以 `skill_path` 視為遠端可控的輸入。程式本來就有「必須在工作目錄內」的檢查（`0405dfd`），但寫法是對 `normcase(...)` 的結果做 `startswith`，CodeQL 認不出它是守衛；而且守衛只涵蓋符號連結解析前的路徑，工作目錄內的連結或 `SKILL.md` 符號連結仍可指向目錄外。

**做法**：
- 先對請求路徑做 `normpath`＋`startswith`（以工作目錄為基準，相對路徑也可），再用 `realpath` 解開符號連結後複查一次，最後 `SKILL.md` 解開符號連結後也必須留在工作目錄內；任何一步超出範圍回 403。判斷用的路徑一律是被檢查過的同一個值（沿用 2026-10-24 SPA 路由「`normpath`＋`startswith` 後再以 `realpath` 複查」的寫法）。
- 預設綁定位址不改：`docs/DOCKER_DEPLOYMENT.md` 的容器部署範例以 `--host 0.0.0.0` 啟動，改預設會破壞該用法；要限制對外可達性請設 `EMBEDDING_HOST=127.0.0.1` 或放在有驗證的反向代理後面。
- 測試：`tests/test_embedding_server.py` 新增 `..` 穿越、絕對路徑在目錄外、目錄符號連結（沒有符號連結權限時改用 Windows 連接點）逃逸、`SKILL.md` 解析後在目錄外、工作目錄內相對路徑等案例（共 6 個測試）。

**待重掃**：此 commit 尚未推送，CodeQL 是否認得新寫法要看推送後的 run。若 #84／#85 仍 open，改以 `false positive` 關閉並附上述測試作為證據（與 2026-10-25 的處置相同）；在重掃結果出來之前，本條不算警示已關閉。

**chromadb（Dependabot #115 critical、#224 critical、#222 high、#223 high，`uv.lock`）**：2026-10-28 重新查證，PyPI 最新版仍是 1.5.9，四筆的 `first_patched_version` 都是空的；`uv lock --upgrade-package chromadb --dry-run` 回報 `No lockfile changes detected`，沒有可升的版本。延後理由與 2026-09-29 相同（漏洞在 ChromaDB HTTP 伺服器，本專案從不啟動 ChromaDB HTTP 伺服器，只用 `HttpClient` 或內嵌的 `PersistentClient`（`cli/adaptors/chroma.py:289,310`；後者在行程內執行 Chroma 引擎，但不對外提供 HTTP））。警示維持 open、不 dismiss；若維護者決定 dismiss，建議理由為 `tolerable_risk`。**重新評估觸發條件**：PyPI 出現 chromadb > 1.5.9 的版本（或四個 GHSA 任一出現 patched version），或本專案開始自己啟動／打包 ChromaDB 伺服器（`chroma run`、`chromadb.server`），或 `cli/adaptors/chroma.py` 預設改成連對外的 `HttpClient`。


## 2026-11-02：上游 PR #478–#479 與 issue #480

三個項目都取目前的 head 讀完 diff，並用 `grep -nE '\S\s{40,}\S|eval\(|new Function|globalThis|[A-Za-z0-9+/]{120,}'` 掃隱藏內容，無命中。commit 軸無新增（仍是 `d26c2e3`）。

| 項目 | 狀態與 head | 裁決 | 證據與理由 |
| --- | --- | --- | --- |
| PR #478（剝掉標題的 `a.headerlink` ¶） | open，`85cd5ad`，+55／-2，4 檔 | **採用（移植）** | 缺陷在本 fork 存在：`doc_scraper.py` 的 `extract_content` 與 `_extract_html_as_markdown` 都直接 `clean_text(h.get_text())`，沒有處理 headerlink。照 PR 做法加 `_heading_text()`、帶入其 fixture 與 3 個測試；CHANGELOG 段落因本線 Unreleased 已有條目，改為手寫一行。觸發重看：上游合併時內容若與 `85cd5ad` 不同，比對 `_heading_text()`。 |
| PR #479（參考檔依頁面順序交錯文字與程式碼） | open，`f7a121a`，+147／-30，4 檔 | **條件式（釘 monitored）** | 缺陷存在（`create_reference_file` 在 `doc_scraper.py:2057` 把程式碼集中到 `**Examples:**` 且只取前 4 個），但它改變所有 reference 檔的輸出版型與 `body_blocks` 資料形狀，屬產品主流程；PR 自己的核取清單「測試全過」「相依已合併」也未勾。等上游合併再隨 commit 軸同步。觸發重看：head 不再是 `f7a121a` 或狀態離開 open（`monitored` 會報）。 |
| issue #480（Claude 增強固定送 `temperature=0.3`） | open，無留言、無對應 PR | **採用（最小修）** | 缺陷存在：`adaptors/base.py:244` 預設 `temperature=0.3`，`claude.py` 的 `enhance()` 沒覆寫；`gemini.py:310` 早已傳 `None`。Claude 路徑改傳 `temperature=None`（`AgentClient` 在 `None` 時不帶該參數，見 `agent_client.py:818`），新增 `test_claude_enhance_sends_no_temperature`。未動 OpenAI 相容路徑（`openai_compatible.py:249`），那條沒有被回報。 |

驗證：新舊相關測試（`test_heading_headerlinks.py`、`test_enhance_via_agent_client.py`、`test_scraper_features.py`）全過；`test_claude_adaptor.py` 的 3 個 upload 測試在乾淨環境（anthropic 2.x）失敗，與本次改動無關（未碰 upload 程式碼）。

## 2026-11-10：上游 PR #482–#483 與 issue #481

三個項目都取目前的 head 讀完 diff（`gh pr diff`，#482 共 164 行、#483 共 472 行），並用 `grep -nE '\S\s{40,}\S|eval\(|new Function|globalThis|[A-Za-z0-9+/]{120,}'` 掃隱藏內容，兩份 diff 皆無命中；兩個 PR 與 issue 均無留言與 review。commit 軸無新增（仍是 `d26c2e3`）。#483 的 diff 內含 #482 全部四個檔案（疊在 #482 之上）。

| 項目 | 狀態與 head | 裁決 | 證據與理由 |
| --- | --- | --- | --- |
| PR #482（workflow 增強：context 傳遞、寬鬆代換、dry-run 修復、深度優先驗證） | open，`eaeb401`，+86／-13，4 檔 | **部分採用（移植兩處缺陷修正），其餘條件式（釘 monitored）** | 移植：`workflow_runner.py` 的 `--workflow-dry-run` 呼叫 `engine.preview()`，本 fork 的 `WorkflowEngine` 沒有此方法，補回；`_run_custom_stage` 原本用 `str.format(**context)`，prompt 內的 JSON 字面大括號會讓代換全部失效，改為只代換 `{var}` 形式且存在於 context 的欄位。兩者各有先紅後綠測試（`tests/test_workflow_preview_substitution.py`）。未移植：`create_command._run_workflows` 傳入 skill 目錄 context、`default.yaml` 的 `skill_polish` 提示詞改寫、`enhance_skill_local` 的驗證段落改寫（A/B/C 標註、`SHRINK_LOG.md`、`EVAL.md`）。這三者改變增強輸出的行為與提示詞設計，不是缺陷修正，且 PR 自述驗證只有 `py_compile` 與一次 mock 執行。觸發重看：PR 合併進上游 `main`，或 head 不再是 `eaeb401`／狀態離開 open（`monitored` 會報）。fork 對上游檔的改寫登記：`enhancement_workflow.py` 的 `preview()` 與代換邏輯是 PR 內容的子集，措辭自寫。 |
| PR #483（文件型 SKILL.md 範本：資料驅動的 When to Use、無空 Quick Reference） | open，`ebed7f5`，+171／-88，16 檔 | **條件式（釘 monitored）** | 缺陷描述屬實（模板文字對所有文件相同），但修法改變 `document_skill_builder.py` 與 PDF 的 SKILL.md 輸出，並重生 9 份 golden；屬產品輸出版型，且疊在未合併的 #482 之上（PR 自述為其後續）。等 #482 與本 PR 合併後隨 commit 軸同步。觸發重看：head 不再是 `ebed7f5` 或狀態離開 open。 |
| issue #481（WebVTT 只有數字的 cue 被丟掉） | open，無留言、無對應 PR | **採用（最小修）** | 缺陷存在：`video_transcript.py` 的 `parse_vtt` 在 cue 內一律略過 `isdigit()` 的行，把 `2026` 這種內文當成 cue 識別碼。改為只有「下一行是時間行」時才視為識別碼，新增 `tests/test_vtt_numeric_cue.py`（無空行分隔的識別碼仍被略過）。 |

驗證：先紅——新增的三個測試修補前失敗（`test_preview_lists_stages_without_calling_ai`、`test_custom_prompt_keeps_literal_json_braces_and_substitutes_context`、`test_numeric_only_cue_text_is_kept`），修補後與 `test_workflow_runner.py`、`test_workflow_prompt_injection.py`、`test_workflows_command.py`、`test_video_scraper.py` 合跑 309 passed、7 skipped（OpenCV 不可用）。

## 2026-11-04：Dependabot PR #23／#24、11-03 起的新警示，與 Python 3.10 跟隨上游的查證

**PR**：#23（pyasn1 0.6.4 → 0.6.5）、#24（pypdf 6.21.2 → 6.21.4）都是 patch 升版、只改 `uv.lock`，CI（Windows py3.11–3.14、Python security scan、CodeQL）全綠，以 squash 合併（`e68e951`、`17b9dc6`），涵蓋 pypdf 7 筆、pyasn1 4 筆警示。

**其餘新警示（皆為 `uv.lock`，除 minimatch 外）**：以 `uv lock --upgrade-package <套件>==<版本>` 一次升級，鎖檔差異只有這四個套件（另有檔頭 `revision` 由 Dependabot 寫的 5 變成本機 uv 寫的 3，與 `7393009` 相同，不影響內容）、來源皆為 PyPI；`requirements.txt` 沒有這些套件的 pin，不需修改。

| 套件 | 版本 | 警示 | 備註 |
| --- | --- | --- | --- |
| filelock | 3.20.3 → 4.2.1 | medium 2（#458、#459） | 大版本，但只是 `huggingface-hub`、`torch` 的傳遞依賴，`src/`、`tests/` 沒有直接使用；兩者都沒有限制 `filelock<4`。以 `huggingface-hub 1.33.0`（鎖檔版本）＋ `filelock 4.2.1` 實跑 `FileLock` 與 `WeakFileLock` 取得／釋放鎖通過 |
| langgraph | 1.2.12 → 1.2.14 | medium 1（#457） | patch |
| langgraph-sdk | 0.4.5 → 0.4.6 | medium 1（#456） | patch |
| joserfc | 1.7.5 → 1.7.6 | medium 1（#460） | patch |

**延後：minimatch（2026-11-07 更正：3.1.5 不在受影響範圍）（#455，2026-11-06 撤回後以同一 GHSA-g3hv-75wg-m249 重開為 #488；medium，`ui/package-lock.json`，開發期傳遞依賴）**：唯一修補版是 11.0.1（2026-10-27 發布），3.x、9.x、10.x 都沒有回補。鎖檔裡的 `minimatch 3.1.5` 來自 `eslint 9.39.2`、`@eslint/eslintrc`、`@eslint/config-array`（`^3.1.2`），`9.0.9` 來自 `@typescript-eslint/typescript-estree 8.52.0`（`^9.0.5`）；即使升到目前最新的 `eslint 10.14.0`、`typescript-estree 8.72.1`，需求也只到 `^10.2.x`，仍在受影響範圍內。用 `overrides` 強制 11.x 會跨兩到三個大版本（3.x 是 CommonJS 預設匯出函式，11.x 是 ESM 具名匯出），會讓 lint 工具鏈壞掉，故不做。弱點是 glob 樣式展開的阻斷服務，輸入是本專案自己的 lint 設定與檔案路徑，不接收外部輸入，也不進 HUD 執行期。警示維持 open，不 dismiss。**觸發條件**：`eslint` 或 `typescript-eslint` 的版本改依賴 `minimatch >=11.0.1`，或 3.x／9.x／10.x 出現修補版。

**延後：chromadb 4 筆（#115、#222–#224）**：PyPI 最新仍是 1.5.9，`first_patched_version` 皆空，理由與觸發條件沿用 2026-10-28 條目，不變。

**Python 3.10 與上游 Windows 新測試失敗（維護者 11-04 指示「跟隨上游」）的查證**：
- 上游 `main`（`d26c2e3`）與 `development`（`5b5d8df`）今天重查都仍是 `requires-python = ">=3.10"`，`tests.yml` 矩陣 `['3.10', '3.11', '3.12']`（ubuntu／macos），`test-vector-dbs.yml` 測 `3.10`、`3.12`。上游沒有停 3.10。
- 本 fork 已在 2026-10-25 依維護者決定停 3.10（`requires-python >=3.11`），當時 Pillow 82 筆警示已全數關閉，現在沒有任何 3.10 相關的延後警示。「上游停了就跟著停、Pillow 延後一併關」這條路徑不成立（上游沒停，fork 也早已沒有該延後）。
- 字面上「跟隨上游」等於恢復 `>=3.10`：Pillow 13.0.0 仍只支援 3.11+，恢復後 `uv.lock` 與 `requirements.txt` 的 3.10 分支會回到 Pillow 12.3.0，約 82 筆 Pillow 警示會重新開啟且沒有修補版。維護者同日確認要恢復，見下一條「2026-11-04（續）」。
- 上游 Windows 新測試失敗：上游 CI 只跑 ubuntu／macos，不測 Windows；跟隨上游即維持 2026-10-24 條目的「不修上游的 Windows 不相容測試」，不變。

## 2026-11-04（續）：恢復 Python 3.10 支援，跟隨上游

**決定**：維護者決定 Python 最低版本跟隨上游。上游 `main`（`d26c2e3`）與 `development`（`5b5d8df`）都是 `requires-python = ">=3.10"`，本 fork 改回 `>=3.10`，取代 2026-10-25「放棄 Python 3.10 支援」條目（`7393009`）。上游 Windows 新測試失敗也跟隨上游：上游 CI 不測 Windows，本 fork 不另外修，維持 2026-10-24 條目的做法。

**做法**：以 `git revert` 還原 `7393009` 的程式與設定變更，逐一對齊上游：
- `pyproject.toml`：`requires-python >=3.10`、恢復 3.10 classifier 與 `tomli; python_version < '3.11'`、ruff `target-version = "py310"`（移除只為 3.11 加的 `UP042` 忽略）、mypy `python_version = "3.10"`；`mypy.ini` 同步。
- CI：`ci.yml` 矩陣恢復 3.10（3.10–3.14）；上游工作 `tests.yml`、`test-vector-dbs.yml`、`release.yml` 回到與上游相同的 3.10 設定。`tools/dev_check.ps1` 的 ruff 目標改回 `py310`；`render.yaml` 的 `PYTHON_VERSION` 回到上游的 3.10。
- 程式：`_version.py` 恢復 `tomli` 退路，`doctor` 版本檢查回到 3.10，以及 `7393009` 用 pyupgrade 改的寫法。`embedding/server.py` 不還原：`7393009` 在這檔只拿掉多餘的 `"r"`，之後的路徑安全修正（2026-10-28）保留。10-25 之後新增的程式已查過，沒有只在 3.11 才有的語法或模組（`tomllib`、`datetime.UTC` 兩處都有 3.10 退路）。
- 文件：README 各語言、`docs/`、安裝腳本、`FORK.md` 的版本說明改回 3.10+；`docs/fork/ROADMAP.md`、`docs/UPSTREAM.md` 的「本線維持 3.11」說法改為跟隨上游。歷史紀錄（CHANGELOG、舊 DECISIONS 條目）不改。
- 鎖檔：`uv lock`（不升級），只把 3.10 需要的分支加回來：Pillow 12.3.0、filelock 4.1.0、networkx 3.4.2、numpy 2.2.6、scikit-learn 1.7.2、scipy 1.15.3（3.11+ 那一支維持原版本），另加回 async-timeout、backports-asyncio-runner、exceptiongroup、importlib-metadata、zipp。`requirements.txt` 的 Pillow 拆回 `13.0.0; python_version >= "3.11"` 與 `12.3.0; python_version < "3.11"`。

**接受的後果（延後，無修補版）**：
- **Pillow 在 Python 3.10**：修補版 13.0.0 的 `requires_python` 為 `>=3.11`，3.10 分支只能停在 12.3.0，`uv.lock` 與 `requirements.txt` 的 Pillow 警示重新開啟，推送 `4e9e9ff` 後實際為 82 筆（兩份清單各 41 筆）。警示維持 open，不 dismiss。
- **filelock 在 Python 3.10**：修補版 4.2.1 的 `requires_python` 為 `>=3.11`，3.10 分支停在 4.1.0。推送 `4e9e9ff` 後實際重開 17 筆（#458、#459，以及 11-04 新開立（advisory 於 10-23／10-28 公布）、範圍涵蓋 4.1.0 的 #472–#486；high 1、medium 11、low 5），修補版都是 4.2.1，而 4.1.1 起全部要求 `>=3.11`，3.10 沒有可裝的修補版。filelock 只是 `huggingface-hub`、`torch` 的傳遞依賴。
- 其他 3.10 分支的舊版本（networkx、numpy、scikit-learn、scipy）若出現警示，同樣依本條處理。
- **觸發條件**：上游停止支援 Python 3.10（`requires-python` 提高或 CI 矩陣移除 3.10）時跟著停，屆時參考 `7393009` 重做；或 Pillow／filelock 發布支援 3.10 的修補版時升級。

**branch protection**：2026-10-25 條目提到的必要檢查 `test (windows / py3.10)` 會因 CI 矩陣恢復而重新出現，不再一直 pending。

## 2026-11-07：Dependabot 兩個失敗 job（minimatch、filelock）與 oauthlib／minimatch 修補

**失敗原因（Dependabot run 42209416543、42209416317，皆 `security_update_not_possible`）**：
- `npm_and_yarn in /ui for minimatch`：`@typescript-eslint/typescript-estree 8.52.0` 以 `^9.0.5` 需要 minimatch，Dependabot 只肯在父套件範圍內升級（最高 9.0.9），而修補版是 11.0.1，它的替代路徑要把 `typescript-eslint` 從 8.52.0 降到 8.36.0，所以放棄。這是 Dependabot 的限制，不是套件沒有修補版。
- `uv in /. for filelock`：Python 3.10 分支只能裝 filelock 4.1.0（4.1.1 起要求 `>=3.11`），修補版 4.2.1 被 3.10 過濾掉（log：`Filtered out filelock 4.1.2 because python requirement >= 3.11 is not satisfied by python 3.10.22`）。這就是 2026-11-04（續）已接受的延後，原因沒變。

**minimatch（#488，GHSA-g3hv-75wg-m249／CVE-2026-118764，medium，影響 `>=7.0.0 <11.0.1`，修補版 11.0.1）— 修補，取代 2026-11-04 的延後**：
- 重新查鎖檔：真正落在影響範圍的只有 `typescript-estree` 底下那一份 9.0.9；`eslint`、`@eslint/config-array`、`@eslint/eslintrc` 用的 3.1.5 低於 7.0.0，不在範圍內。先前「用 overrides 會讓 3.x 跨三個大版本」的顧慮不適用於這個警示。
- 做法：`ui/package.json` 加範圍限定的 `overrides`，只在 `@typescript-eslint/typescript-estree` 之下覆寫 `minimatch` 為 `11.0.1`（第一個修補版，2026-10-27 發布，已超過 10 天），並把它新帶的 `@isaacs/nonrecursive-glob-match` 釘在 `1.0.3`（2026-10-28 發布；`1.1.0` 於 2026-11-05T21:38Z 才發布，未滿冷卻期，且 minimatch 11.0.1 只要求 `^1.0.1`）；不動 3.1.5 那一份。巢狀 override 有生效。`npm install --package-lock-only` 重產鎖檔，差異只有 minimatch 9.0.9 → 11.0.1，加上它新帶的依賴，三個新套件都在 `typescript-estree/node_modules` 之下、沒有被提升到頂層：`brace-expansion` 2.1.7 → 5.0.12（2026-09-14 發布）、`balanced-match` 新增 4.0.4（2026-02-22 發布）、`@isaacs/nonrecursive-glob-match` 新增 1.0.3（2026-10-28 發布）。
- 驗證：`npm ci`、`npm run lint`、`npm run build` 全過，`npm audit` 0 筆。`npm test`（playwright）需要瀏覽器與後端，未跑。
- 取捨：`ui/package.json` 因此多一個 `overrides` 區塊，與上游 `ui/` 有差異。**觸發條件**：`typescript-eslint` 改依賴 `minimatch >=11.0.1` 時移除 `overrides`。

**oauthlib（#487，GHSA-3jp2-3mrg-2vxc／CVE-2026-49272，high，影響 `>=3.3.0 <4.0.1`，修補版 4.0.1）— 修補**：`uv lock --upgrade-package oauthlib==4.0.1`，鎖檔只有 oauthlib 4.0.0 → 4.0.1 三行（PyPI 發布於 2026-10-31，`requires_python >=3.9`，3.10 分支也適用）。與 Dependabot PR #29 目標版本相同，但 #29 另把 `revision` 改成 5 並重解 onnxruntime 等（+90/−8）；本次是最小差異，推送後以 superseded 關閉 #29。#29 的 CI（CI、CodeQL）全綠。

**filelock 延後清單**：#458、#459、#472–#486 維持延後，理由與觸發條件同 2026-11-04（續）。Pillow 與 chromadb 同樣不變。

## 2026-11-08：依維護者指示 dismiss 無法處置的 Dependabot 警示

**決定**：維護者 2026-11-08 指示「告警沒必要開著的就關」。這取代 2026-09-29、2026-10-28、2026-11-04（續）、2026-11-07 各條目中「警示維持 open，不 dismiss」的規則：無法處置的警示一律 dismiss 並附理由與重開條件；可修的仍然先修。

**查證（2026-11-08）**：
- `requirements.txt` 已拆開：`Pillow==13.0.0; python_version >= "3.11"` 與 `Pillow==12.3.0; python_version < "3.11"`。`uv.lock` 的 pillow 12.3.0 只掛 `python_full_version < '3.11'`，13.0.0 掛 3.11+ 各分支；filelock 同理（4.1.0 只掛 `< '3.11'`，其餘 4.2.1）。3.11+ 路徑早已是修補版，沒有可再修的地方。
- 修補版 Pillow 13.0.0、filelock 4.2.1 的 `requires_python` 都是 `>=3.11`；上游 `main`、`development` 仍是 `requires-python = ">=3.10"`；chromadb PyPI 最新仍是 1.5.9，`first_patched_version` 為空。
- 警示實際為 open 103 筆，不是原先估計的 58：Pillow 82（`requirements.txt` 41、`uv.lock` 41）、filelock 17、chromadb 4。minimatch #488 已是 fixed（`4db4193` 的 `overrides`），不在 open 清單。

**處置（全部 `tolerable_risk`，皆附理由與重開條件）**：

| 群組 | 筆數 | 理由 | 重開條件 |
|------|------|------|----------|
| Pillow（`requirements.txt` 41、`uv.lock` 41） | 82 | 3.10 分支只能停在 12.3.0，修補版 13.0.0 需 Python >=3.11；3.11+ 已是 13.0.0；上游仍支援 3.10 | 本 fork 停 3.10（`requires-python` 提高並移除 3.10 分支），或 Pillow 對 12.x 回補修補版 |
| filelock（`uv.lock`：#458、#459、#472–#486） | 17 | 3.10 分支只能停在 4.1.0，修補版 4.2.1 需 >=3.11；3.11+ 已是 4.2.1；只是 `huggingface-hub`、`torch` 的傳遞依賴 | 同上，或 filelock 發布支援 3.10 的修補版 |
| chromadb（`uv.lock`：#115、#222–#224） | 4 | 無修補版；漏洞在 ChromaDB HTTP 伺服器，本專案只當用戶端、不啟動伺服器（見 2026-09-29、2026-10-28 條目）。GitHub 沒有 `vulnerable_code_not_used` 選項，故用 `tolerable_risk` | chromadb 發布 > 1.5.9 的版本，或本專案開始自行啟動 ChromaDB 伺服器 |

dismiss 後 open 為 0。dismiss 是對現有警示的處置，不改任何程式或鎖檔；之後 3.10 分支的 networkx、numpy、scikit-learn、scipy 若再出現警示，同樣先確認 3.11+ 路徑已是修補版，再依本條 dismiss。**重開方式**：條件成立時在 GitHub 重開該警示，或停 3.10 時直接升級後由重掃關閉。

## 2026-11-10：fork 自己的產品測試 job（`fork-product-tests.yml`）

**缺口**：上游 `tests.yml` 的每個 job 都有 `if: github.repository == 'yusufkaraaslan/Skill_Seekers'`，fork 上整份被略過（檔內沒寫理由；從內容看是它用 ubuntu／macOS 矩陣、Codecov 上傳、Playwright 瀏覽器與 `ui/` 建置，不是為 Windows fork 設計的）。`ci.yml` 跑 `tools/dev_check.ps1`，只測 `tools/tests`。結果是 fork 改 `src/`（`28d65ab`、`c709c93`、CodeQL 修補）時，新增的 `tests/` 測試只在本機驗過，CI 沒有人跑。

**決定**：新增 `.github/workflows/fork-product-tests.yml`（`if: github.repository == 'SanHsien/Skill_Seekers'`，`windows-latest`、Python 3.12），不動 `tests.yml`。依賴用 `uv sync --locked --extra mcp --extra ui`（與 `ci.yml` 的 security job 同一個 uv 版本與鎖檔做法，避免另一套浮動版本）。action 釘 SHA、`permissions: contents: read`、`timeout-minutes: 25`、`concurrency` 照 `ci.yml`。

**範圍：明確清單，不是整個 `tests/`**。清單在 `tools/fork_product_tests.txt`（21 檔），內容是 `git log` 查到的 fork 作者提交（`7d055a8`、`a554f53`、`e2aea07`、`8e8c736`、`0f44a45`、`a45d142`、`0405dfd`、`9b15bc0`、`28d65ab`、`c709c93`）新增或修改的測試檔，加上同模組的鄰近測試（workflow、video、path safety）。再加 marker 篩選 `not integration and not e2e and not network and not slow`。理由：

- 在 `8eaff3f` 上以相同 marker 跑整個 `tests/`：116 failed、1 error、4297 passed、82 skipped，耗時 7 分 41 秒；失敗包含 `test_web_*`、`test_marketplace_publisher.py`，另有 `test_bootstrap_skill.py` 的 1 個 error，且 `test_web_regressions.py` 會寫入真實的使用者 skills 目錄（`FileExistsError: ...\.claude\skills\demo already exists`）。把整套放進 CI 不是「補覆蓋」，是一條天天紅、又吃 8 分鐘的 job，紅燈會被習慣性忽略。另一次把 `HOME`／`USERPROFILE` 指到暫存目錄重跑，在 `test_mcp_fastmcp.py` 卡住超過 6 分鐘無輸出，需手動終止。
- 清單子集（含 `tests/test_vtt_numeric_cue.py`、`tests/test_workflow_preview_substitution.py`）以 CI 同一組指令在 Python 3.12 跑：660 passed、7 skipped（OpenCV 不可用）、25 deselected，pytest 計時 22.6 秒。

**刻意排除 `tests/test_web_api.py`**（fork 在 CodeQL 修補時改過它）：12 個測試在 Windows 失敗，原因是 fixture 只設 `HOME`（`monkeypatch.setenv("HOME", ...)`），而 Windows 的 `Path.home()` 讀 `USERPROFILE`（實測 `HOME=/x/fake USERPROFILE=C:\real` 時回傳 `C:\real`），所以隔離不成立、測到的是真實使用者目錄。這是上游測試對 POSIX 的假設，不是產品缺陷；改上游測試會與上游分歧。觸發重看：上游 fixture 改成同時設 `USERPROFILE`，或本 fork 決定加 ubuntu 腿專跑該檔。

**其他取捨**：只跑 Python 3.12 一格（`ci.yml` 已用 3.10–3.14 矩陣驗證 `tools/tests`；產品測試每多一格多 25 秒以上，但本機只驗過 3.12／3.13，未驗證的格子不先放進去）。不安裝 `pytest-timeout`（不在 `uv.lock` 內，為此另裝浮動版本會破壞 `--locked`）、不用 `scripts/run_tests_safe.py`（它是為記憶體受限的上游 runner 寫的守衛）；job 的 `timeout-minutes` 是上限。清單新增規則：fork 提交新增或修改 `tests/` 檔時，同一個 commit 把它加進 `tools/fork_product_tests.txt`；`tools/tests/test_fork_product_tests_workflow.py` 釘住「清單檔案都存在、不重複、保留這批移植測試」與 workflow 的守衛、Windows runner、SHA 釘選、最小權限。

**家目錄隔離（追加）**：獨立審查實跑時，清單內測試會寫 `.cache/skill-seekers/embeddings/embeddings.db`、`.config/miopen` 到家目錄；本機用同指令重跑也曾寫壞真實的 `~/.claude/skills/demo`。job 因此把 `HOME`、`USERPROFILE` 指到 `runner.temp` 下的 `home` 並先建立；主 `uv run` 明寫 `--python 3.12`；清單讀取先 `Trim()` 再略過空行與 `#`，與 `_listed_tests()` 一致。本機重跑請同樣把兩個變數指到暫存目錄。

**`pytest.ci.ini` 的說明**：它是上游檔，沒有被任何 workflow 引用，本 fork 不改。它 collect 0 個測試的正確原因是 ini 格式不認 TOML 清單語法：`testpaths = ["tests"]` 被當成字面字串 `["tests"]`（同理 `python_files`、`python_classes`），所以找不到路徑，與測試本身無關。


## 2026-11-12：唯讀覆核 F1–F7 修補（fork 修補登記）

**決定**：依唯讀品質覆核（固定 HEAD `1ec4ec1`）逐項修補。核對 `upstream/main`（`d26c2e3`）與 `upstream/development`：兩者的 `doc_scraper.py`、`llms_txt_downloader.py`、`skill_converter.py`、`notion_scraper.py`、`enhancement_workflow.py` 皆未含這些修補，故全部登記為 fork 修補，**不回貢**（回貢需維護者在當次對話明確同意）。

| 嚴重度 | 項目 | 修補 commit | 紅燈測試（先失敗） |
| --- | --- | --- | --- |
| 高 | F1 URL 分類在 Windows 穿越 references/ | `49c6c56` | `test_three_hostile_url_segments_cannot_write_outside_references`：檔案寫到輸出目錄的上一層 |
| 高 | F3 來源指示進入 SKILL.md 正文、圍欄被提前關閉 | `fe3560c` | `test_source_instructions_stay_inside_fenced_data_blocks`、`test_code_fence_breakout_in_source_cannot_close_the_block_early`、`test_source_provenance_is_recorded_next_to_copied_text`、`test_frontmatter_description_cannot_inject_keys_or_lines` |
| 中 | F2 自訂 llms_txt_url 檔名含反斜線 | `d7857db` | `test_llms_txt_url_filename_cannot_carry_windows_traversal` |
| 中 | F5 Windows 根磁碟 `--output` 被裁成 drive-relative | `4bd080a` | `test_drive_root_output_keeps_its_root_anchor` |
| 中 | F4 Notion 429 重試無上限 | `119850c` | `test_persistent_429_gives_up_after_bounded_retries`（另有總等待與恢復案例） |
| 中 | F6 Windows 回歸測試未涵蓋資料流 | `91561ae` | 把新測試列入 `tools/fork_product_tests.txt`，並加入 `REQUIRED_PORTED_TESTS` |
| 低 | F7 提示詞代換破壞 str.format 語法 | `b46c6cf` | `test_custom_prompt_keeps_str_format_escapes_conversions_and_specs` |

**驗證（2026-11-12 最終，`eab3af7` 之後）**：指令為 `python -m pytest <tools/fork_product_tests.txt 內的檔案> -m "not integration and not e2e and not network and not slow" -q`，HOME／USERPROFILE 指向暫存目錄，PYTHONUTF8=1。結果：780 passed、7 skipped、25 deselected、0 failed。`tools\dev_check.ps1` exit 0，結尾 `WINDOWS DEV CHECK GREEN`；`--strict` exit 0；`git diff --check` 無輸出。

**獨立審查的不同結果**：審查者以同一清單全跑（未套用上述 marker）得 789 passed、8 skipped、2 failed，兩個失敗皆在 `tests/test_real_world_fastmcp.py`，審查者判定 1ec4ec1 基底即失敗，原因為 cp950 編碼與品質分數既有問題。本機以上述 UTF-8 環境單獨執行該檔：5 passed、1 skipped；以 marker 執行則全數 deselected。本次未重現那兩個失敗，兩份數字的差異來自執行環境與 marker，未另行證實。

**現況（取代先前「未完成／限制」列表）**：

- F1：寫入點檢查由 `resolve_reference_path()` 統一處理（`49c6c56`、`4a0d827`）。
- F2：llms 三個寫入點改走 `resolve_reference_path()`，有 realpath containment（`4a0d827`）；檔名另由 downloader 清理（`d7857db`）；Windows 裝置名與雙向控制字元在 `eab3af7` 拒絕。
- F3：SKILL.md 的模式、範例與 frontmatter 以動態圍欄（`fe3560c`）；`references/*.md` 的頁面內文圍欄並標示為來源資料，標題、URL、heading 壓成單行（`4a0d827`）；推斷的 description 壓成單行，含 Markdown 語法時圍欄（`4a0d827`）。
- F4：固定 10 秒改為讀 `Retry-After`，仍受總等待上限約束（`8d40acd`）。
- F5：單一磁碟字母根（`4bd080a`）與 UNC 共享根（`a9108e2`）皆保留根錨點。
- F7：`:spec` 等效果只在 `str.format` 可解析的模板生效；無效模板的 fallback 仍不套用 `:spec`，維持 c709c93 的既有行為（`b46c6cf`）。
- 上游 `--strict` 紅燈已於同日的上游分流處理（見下方同日條目）。
- `tests/test_sentence_transformers_security.py` 仍因未安裝 `sentence_transformers` 而 skip（既有狀態）。

## 2026-11-12：上游 PR #484、#486 與 issue #485（三項延後）

三個項目都讀過內容：PR #484 與 #486 用 `gh pr diff` 取得 diff（唯讀），issue #485 讀 body。掃描隱藏內容的結果：兩份 diff 的不可見或格式字元（Unicode Cf、Co、控制字元）皆為 0；上游 comments 與 reviews 皆為空。commit 軸無新增（仍是 `d26c2e3`）。

| 項目 | 狀態與 head | 裁決 | 證據與理由 |
| --- | --- | --- | --- |
| PR #484（PDF 程式碼偵測：不把文件片段標成 sass／typescript） | open，`2f35172`，+231／-35，3 檔（2 修改、1 新增測試） | **延後（條件式，釘 monitored）** | 缺陷屬實，修法有測試。這次無法在本機套用上游 diff，權限系統拒絕了 `git apply` 這個動作，因此沒有做先紅後綠的移植。另一個理由：sass 規則改為行首錨點，會改變語言偵測的全域行為，需要獨立的移植批次審查。觸發重看：移植批次開始；或 head 不再是 `2f35172`、狀態離開 open（`monitored` 會報）。 |
| PR #486（install-agent 安裝目錄名改用 SKILL.md frontmatter 的 name） | open，`d5a6088`，+73／-1，2 檔 | **延後（條件式，釘 monitored）** | 缺陷描述可信（打包時的 `-opencode` 後綴與目錄名要求不一致）。同樣因為權限拒絕，這次未套用 diff，未移植。觸發重看：移植批次開始；或 head 不再是 `d5a6088`、狀態離開 open。 |
| issue #485（PDF 字型路徑缺結構驗證、品質分數膨脹、未使用 TOC） | open，無留言、無對應 PR | **延後（不釘 monitored，監看 #484）** | 三項中第一、二項需要設計門檻（code 形狀、分數規則），不是單點修正；第三項是功能缺口。#484 合併後若真實案例仍有片段被當成程式碼，再另開設計。 |

水位：`reviewed_pr_through` 483 → 486，`reviewed_issue_through` 481 → 485（對應 `tools/upstream_baseline.json`）。`monitored` 新增 `pr#484`、`pr#486`。`reviewed_through`（commit 軸）未變。

**限制**：三項皆未移植，fork 的 PDF 與 install-agent 行為與上游一致、仍含上述缺陷。若維護者要求移植，應在另一批次先紅後綠處理，並在該批次記錄新的 head。

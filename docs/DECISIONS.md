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

## 2026-11-04：Dependabot PR #23／#24、11-03 起的新警示，與 Python 3.10 跟隨上游的查證

**PR**：#23（pyasn1 0.6.4 → 0.6.5）、#24（pypdf 6.21.2 → 6.21.4）都是 patch 升版、只改 `uv.lock`，CI（Windows py3.11–3.14、Python security scan、CodeQL）全綠，以 squash 合併（`e68e951`、`17b9dc6`），涵蓋 pypdf 7 筆、pyasn1 4 筆警示。

**其餘新警示（皆為 `uv.lock`，除 minimatch 外）**：以 `uv lock --upgrade-package <套件>==<版本>` 一次升級，鎖檔差異只有這四個套件（另有檔頭 `revision` 由 Dependabot 寫的 5 變成本機 uv 寫的 3，與 `7393009` 相同，不影響內容）、來源皆為 PyPI；`requirements.txt` 沒有這些套件的 pin，不需修改。

| 套件 | 版本 | 警示 | 備註 |
| --- | --- | --- | --- |
| filelock | 3.20.3 → 4.2.1 | medium 2（#458、#459） | 大版本，但只是 `huggingface-hub`、`torch` 的傳遞依賴，`src/`、`tests/` 沒有直接使用；兩者都沒有限制 `filelock<4`。以 `huggingface-hub 1.33.0`（鎖檔版本）＋ `filelock 4.2.1` 實跑 `FileLock` 與 `WeakFileLock` 取得／釋放鎖通過 |
| langgraph | 1.2.12 → 1.2.14 | medium 1（#457） | patch |
| langgraph-sdk | 0.4.5 → 0.4.6 | medium 1（#456） | patch |
| joserfc | 1.7.5 → 1.7.6 | medium 1（#460） | patch |

**延後：minimatch（#455，2026-11-06 撤回後以同一 GHSA-g3hv-75wg-m249 重開為 #488；medium，`ui/package-lock.json`，開發期傳遞依賴）**：唯一修補版是 11.0.1（2026-10-27 發布），3.x、9.x、10.x 都沒有回補。鎖檔裡的 `minimatch 3.1.5` 來自 `eslint 9.39.2`、`@eslint/eslintrc`、`@eslint/config-array`（`^3.1.2`），`9.0.9` 來自 `@typescript-eslint/typescript-estree 8.52.0`（`^9.0.5`）；即使升到目前最新的 `eslint 10.14.0`、`typescript-estree 8.72.1`，需求也只到 `^10.2.x`，仍在受影響範圍內。用 `overrides` 強制 11.x 會跨兩到三個大版本（3.x 是 CommonJS 預設匯出函式，11.x 是 ESM 具名匯出），會讓 lint 工具鏈壞掉，故不做。弱點是 glob 樣式展開的阻斷服務，輸入是本專案自己的 lint 設定與檔案路徑，不接收外部輸入，也不進 HUD 執行期。警示維持 open，不 dismiss。**觸發條件**：`eslint` 或 `typescript-eslint` 的版本改依賴 `minimatch >=11.0.1`，或 3.x／9.x／10.x 出現修補版。

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

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


## 2026-10-24：Dependabot 警示重盤（105 筆 open）與 critical／high 修補

**決定**：open 警示由 2026-10-01 的 5 筆增為 105 筆（critical 12、high 54、medium 36、low 3），除 chromadb、Python 3.10 的 Pillow 外全數有修補版。依艦隊規則，有修補版的 critical／high 一律修，改在分支 `security/deps-20261024` 以單一 PR 處理（不 merge、不 dismiss 任何警示）：

| 套件 | 舊版 → 新版 | 清掉的警示 | 備註 |
| --- | --- | --- | --- |
| certifi | 2025.11.12 → 2026.10.19（`requirements.txt` 2025.10.5 → 2026.10.19） | critical 2 | 最小修補版 |
| fsspec | 2026.2.0 → 2026.6.0 | high 1 | 最小修補版 |
| Pillow | 12.3.0 → 13.0.0（僅 Python >= 3.11） | critical 8、high 46、medium 24 | `uv.lock` 與 `requirements.txt` 都以 `python_version` 條件拆開，見下方 Python 3.10 暫緩 |
| nltk | 3.10.3 → 3.10.4 | high 1 | 見下方 |

由 Dependabot 既有 PR 處理、本分支刻意不重複：aiohttp 3.14.3 → 3.14.4（#9，high 3、medium 3、low 2）、GitPython 3.1.62 → 3.2.1（#10，high 1）、opentelemetry-api 1.39.1 → 1.45.1（#11，medium 1）、pypdf 6.19.0 → 6.21.1（#12，medium 7、low 1）。四個 PR 的檢查皆綠，合併它們才算 high 全數清完。multidict（medium 1，修補版 6.9.1）尚無 PR，不在本輪範圍。

**nltk**：2026-09-29 記錄為無修補版。現在 PyPI 有 3.10.4（2026-10-20 發布，變更說明為把模型存取、下載與外部程式路徑全數導入沙箱），而該警示的受影響範圍是 `<= 3.10.3`，3.10.4 已在範圍外，故升級；警示的 `first_patched_version` 仍是空值，是否關閉由 GitHub 重掃決定。這個升級獨立成一個 commit，若發現 llama-index 路徑受影響可單獨還原。

**暫緩（沒有可驗證的修補版）**：

- **chromadb 1.5.9**（critical 2、high 2）：PyPI 最新版仍是 1.5.9，與 2026-09-29 相同，警示 `first_patched_version` 皆為空。理由與限制條件沿用 2026-09-29 的決定（本專案只當用戶端，漏洞在 ChromaDB HTTP 伺服器）。觸發條件不變：chromadb 發布 > 1.5.9 的版本、或本專案開始自己啟動 ChromaDB 伺服器時重評。
- **Pillow 在 Python 3.10**（`uv.lock` 與 `requirements.txt` 的 `python_version < "3.11"` 分支，仍是 12.3.0）：修補版 13.0.0 的 `requires_python` 為 `>=3.11`（PyPI 中繼資料），而 `pyproject.toml` 宣告 `requires-python >=3.10`，CI 矩陣也含 3.10，3.10 沒有可裝的修補版。升級到 13.0.0 需要放棄 Python 3.10 支援，這是產品決策，不在依賴升級範圍。因為鎖檔仍含 12.3.0，這批 Pillow 警示可能在 GitHub 上維持 open。觸發條件：決定放棄 Python 3.10（屆時把 `requires-python` 改為 `>=3.11` 並重新產生鎖檔）、或 Pillow 發布支援 3.10 的修補版時重評。

**驗證**：`uv lock --check` 通過；`tools\dev_check.ps1` 全綠（56 passed、1 skipped）；以 `uv sync --locked`（Python 3.12）安裝後，跑上游 fast 測試指令（`pytest tests/ -n 6 --dist=loadfile -m "not slow and not integration and not e2e and not network and not serial and not mcp_only"`），修補前後各 75 個失敗，失敗集合完全相同（皆為本修補前就存在的失敗，與依賴升級無關）；本 fork 的 CI 不執行這套產品測試。

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


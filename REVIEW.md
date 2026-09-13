# Repository review（Windows-only）

- Review date: 2026-09-12
- Review baseline: `c333a379bfb43f42eb605fd575be955762a9fa7b` (release v3.9.1)
- Remediation: 同日 fork-local overlay（不回貢）
- Upstream reviewed through: `c333a379bfb43f42eb605fd575be955762a9fa7b`
- Primary environment: Windows 11、PowerShell、Python 3.14.7（本機 gate）；產品 Python 要求 `>=3.10`
- Status: 維護骨架與產品相依環境全面可用。已完成建立 Windows 原生門禁與驗收。

## 結論

這個 fork 適合作為 Windows 本機、給 Agent 維護的 Skill_Seekers 線。產品行為跟隨 `yusufkaraaslan/Skill_Seekers` `c333a37`（release v3.9.1），再加上本線維護骨架：繁體中文維護文件、Windows 原生 1-click gate、純 Windows 原生維護 CI、每週上游水位追蹤（commit、PR、issue）以及每月依賴新鮮度檢查。

上游既有的 7 個 GitHub Actions 工作流程皆已配置 `if: github.repository == 'yusufkaraaslan/Skill_Seekers'` 防護，杜絕在 fork 端因欠缺第三方 Token 或 Linux 特有環境而觸發非預期的錯誤。

## 本輪實證

### 審查當下（`c333a37`）

```text
git rev-parse HEAD
→ c333a379bfb43f42eb605fd575be955762a9fa7b

gh repo set-default --view
→ SanHsien/Skill_Seekers
```

實查結果：
- 上游 repository 為 `yusufkaraaslan/Skill_Seekers`，採 MIT License。
- 上游 PR 水位為 `#468`，Issue 水位為 `#469`。
- 上游預設分支為 `development`，本 fork 預設分支確立為 `main`（跟隨穩定發佈線 v3.9.1）。
- 維護工具全面配置 `$env:PYTHONUTF8 = "1"` 與 `$env:PYTHONIOENCODING = "utf-8"`，避免 Windows CP950 解碼異常。

## 已修 findings

| ID | 嚴重度 | 做了什麼 |
|---|---|---|
| R-01 | P2 | `.gitignore` 加入 `.env`、`.venv`、`upstream-review-report.md`、`dependency-freshness-report.md` |
| R-02 | P2 | 建立獨立維護測試目錄 `tools/tests/` 與獨立 `tools/pytest.ini`，避免產品環境污染 |
| R-03 | P2 | 建立 `FORK.md`、`NOTICE.md`、`LICENSE`、`SECURITY.md`、`AGENTS.md`、`CLAUDE.md`、`GEMINI.md`，寫明對外邊界與安全性 |
| R-04 | P2 | 建立 Windows 11 原生開發門禁 `tools/dev_check.ps1` 與環境建置腳本 `tools/bootstrap_dev.ps1` |
| R-05 | P2 | 建立純 Windows 原生 CI 工作流程 `.github/workflows/ci.yml`（Python 3.10~3.14 矩陣） |
| R-06 | P2 | 建立上游更新檢查工具 `tools/check_upstream_updates.py` 與每週排程工作流程 |
| R-07 | P2 | 建立依賴新鮮度檢查工具 `tools/check_dependency_freshness.py` 與每月排程工作流程 |
| R-08 | P2 | 上游 7 個 GitHub Actions 工作流程加上 `if: github.repository == 'yusufkaraaslan/Skill_Seekers'` 條件防護 |
| R-09 | P1 | 修復 `skill-seekers-enhance` 缺乏 `--enhance-level` 參數導致 scraper 轉發時崩潰（對齊上游 PR #465） |
| R-10 | P1 | 修復 `src/skill_seekers/cli/doctor.py` 缺少 `main()` 入口導致 `skill-seekers-doctor` 執行時 `ImportError`（對齊上游 PR #456） |
| R-11 | P0 | 修復 Git 自訂配置快取目錄路徑穿越漏洞（CWE-22），加入 `validate_path_segment` 驗證防止惡意目錄逃逸（對齊上游 PR #464 / Issue #462） |
| R-12 | P1 | 修復 `skill_seekers.cli` 模組頂層無防護引用 `requests` 與 `pydantic`，使輕量環境與 doctor 指令啟動具備容錯能力 |

## 2026-09-13 深度審查與 Bug 修復

- **Tag 清理**：原倉庫包含 36 個 release tag（`v0.3.0` ~ `v3.9.1`）。依指令清理，本機與 GitHub 遠端（`SanHsien/Skill_Seekers`）僅保留最新 tag `v3.9.1`。
- **分支清理**：刪除遠端 26 個多餘分支，僅保留單一主分支 `main`。
- **R-09（PR #465）修復**：`src/skill_seekers/cli/arguments/enhance.py` 補齊 `--enhance-level`，並在 `src/skill_seekers/cli/enhance_command.py` 支援 level 0 跳過邏輯與 list 參數支援。
- **R-10（PR #456）修復**：`src/skill_seekers/cli/doctor.py` 補齊 `main(args=None) -> int` 函式，讓獨立 console script 正常啟動。
- **R-11（PR #464 / Issue #462）安全修復**：`src/skill_seekers/services/git_repo.py` 加入 `validate_path_segment` 函式防範 CWE-22 路徑穿越，並於 MCP 工具同步防護。
- **R-12 修復**：`src/skill_seekers/cli/__init__.py` 頂層對重型依賴（`requests`、`pydantic`）加上 graceful fallback，確保 `skill-seekers-doctor` 診斷工具在缺少依賴時仍可啟動運作。
- **迴歸與合約測試**：`tools/tests/test_fixes.py` 納管以上修復之單元測試，全部通過。

## 接受、不改契約

- 上游既有之多語系文件（`README.zh-CN.md`、`README.ja.md` 等）完整保留，以確保上游相容性。
- `requirements.txt` 保留上游精確鎖定之依賴版本，維護層透過 `requirements-dev.txt` 獨立管理 pytest 與 ruff。

## 尚未宣稱範圍

- 尚未在 Windows 上對所有 18 種數據源轉換流程與本機 40 個 MCP 工具進行端到端 live integration test（此部分依賴特定第三方 API 金鑰如 Anthropic / OpenAI 等）。
- 尚未引進上游 `development` 分支在 v3.9.1 之後的未合併 commit（待上游發布 v3.10.0 正式 release 後由每週上游檢查機制統一評估引進）。

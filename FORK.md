# Fork 維護說明

本 repo fork 自 [`yusufkaraaslan/Skill_Seekers`](https://github.com/yusufkaraaslan/Skill_Seekers)，
沿用 MIT License 與完整 Git 歷史。

## 為什麼維護 fork

- 保留原作者持續更新的 Skill Seekers AI Agent 技能與知識庫轉換層、18 種數據來源輸入、40 個 MCP 工具與多平台打包能力。
- 採 Windows-first 維護：Windows 11 + PowerShell 是主要開發、除錯與完整驗收環境。
- 公開入口維持繁體中文為主，英文鏡像放 [`README.en.md`](README.en.md)。
- 建立可重現的 Windows 開發 gate、Windows CI job，以及逐筆審查的上游追蹤（涵蓋 commit、PR 與 issue 水位）。
- 產品執行路徑以上游為準；本線不發佈第三方套件取代上游官方發布，亦不變更上游授權。

**回貢判準：修的是上游通用 bug 就送回去；這裡獨創的文件與 Windows 維護骨架留在這裡。**
回貢前必須在當次對話取得維護者明確同意；「fork」、「建開發環境」、「開 PR」都不是同意。

## 與上游的差異

| 項目 | 說明 |
|---|---|
| `README.md` | 繁中主檔；加入 fork 維護資訊與快速入口 |
| `README.en.md` | 英文鏡像；加入 fork 維護資訊 |
| `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` | 本 fork 的 AI 維護單一真相源 |
| `NOTICE.md` / `FORK.md` / `LICENSE` | 來源、授權與同步說明 |
| `tools/dev_check.ps1` | Windows 本機一鍵 gate（維護工具，不安裝重型依賴） |
| `tools/bootstrap_dev.ps1` | Windows 本機一鍵初始化與驗收（支援 `-All` 參數安裝產品依賴） |
| `tools/test_product.ps1` | Windows 原生產品冒煙測試執行腳本 |
| `requirements-dev.txt` | 維護依賴清單（pytest, ruff） |
| `.github/workflows/ci.yml` | 純 Windows 原生 CI (windows-latest Python 3.10–3.14 矩陣)：compile / ruff / 維護測試 / 連結檢查 |
| `.github/workflows/upstream-check.yml` | 每週對上游做未審查 commit、PR、issue 水位檢查 |
| `.github/workflows/dependency-freshness.yml` | 每月依賴新鮮度檢查 |
| `.github/workflows/codeql.yml` | CodeQL 安全掃描工作流程 |
| `docs/DECISIONS.md`、`docs/UPSTREAM.md`、`docs/DEVELOPMENT.md` | fork 維護與決策文件 |
| `REVIEW.md` | 全庫風險與審查快照 |

核心代碼與 MCP 工具在 `src/`，以上游為準。

## 分支與 remote

- `origin/main`：SanHsien 維護線，也是唯一長期分支。
- `upstream/main`：上游發佈線（release v3.9.1）。
- `upstream/development`：上游日常開發線。

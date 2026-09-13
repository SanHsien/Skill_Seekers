# AGENTS.md

給 Codex、Claude Code、Cursor、Antigravity 與其他自動化代理在本專案工作時的指引。產品與使用方式先讀 [`README.md`](README.md)；開發與驗收細節見 [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)。

## 專案定位

這是 [`yusufkaraaslan/Skill_Seekers`](https://github.com/yusufkaraaslan/Skill_Seekers) 的 MIT License fork。
核心價值是將多種數據源（文件網站、GitHub 倉庫、PDF 等）轉換為 AI 技能與知識庫轉換層，具備多平台打包與豐富 MCP 工具生態。

`origin` 是 `SanHsien/Skill_Seekers`（預設分支 `main`），`upstream` 是原作者 repo。
保留上游作者、MIT License 與產品程式。本 fork 的維護差異記在 [`FORK.md`](FORK.md) 與 [`docs/DECISIONS.md`](docs/DECISIONS.md)。

## 硬閘門與邊界規範

- **PR、push、release 絕不打回上游**：所有操作只打 `SanHsien/Skill_Seekers`。除非維護者在當次對話明確要求回貢，否則嚴禁向上游開 PR。每個 clone 必須先跑 `gh repo set-default SanHsien/Skill_Seekers` 並以 `gh repo set-default --view` 確認。
- **改動不漫遊專案目錄外**：嚴禁讀寫使用者個人目錄或外部專案。
- **無敏感資料**：API 金鑰、Token、私鑰與個人個資嚴禁進代碼、指令列或提交。
- **回報前必須實證**：回報「完成 / 修好 / 測試通過」之前，必須實際在 Windows 原生環境執行 `pwsh -NoProfile -File tools\dev_check.ps1` 並回貼完整輸出。
- **不虛假過關**：嚴禁註解掉測試、盲目捕獲例外（`except Exception: pass`）或偽造假資料。
- **回覆語系**：回覆一律使用繁體中文；術語與程式碼保持英文原文。先講結論再講細節。

## 開發與門禁指令

```powershell
# 一鍵初始化環境
pwsh -NoProfile -File tools\bootstrap_dev.ps1

# 本機開發門禁（compileall + ruff + pytest + check_links）
pwsh -NoProfile -File tools\dev_check.ps1

# 產品冒煙測試
pwsh -NoProfile -File tools\test_product.ps1
```

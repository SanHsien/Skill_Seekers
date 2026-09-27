# 貢獻指南

歡迎能保住 Windows 相容性、代碼穩定性與低維護成本的小改動。

## 開始前

1. 先讀 [`AGENTS.md`](AGENTS.md)、[`FORK.md`](FORK.md) 與 [`README.md`](README.md)。
2. 確認問題在最新 `main` 仍可重現，並查過既有 Issues。
3. 產品核心行為的實質變更，優先考慮回報或回貢 [`yusufkaraaslan/Skill_Seekers`](https://github.com/yusufkaraaslan/Skill_Seekers)。
4. 不要附上真實使用者個資、專有文件、未經授權的檔案或任何憑證。

## 本機開發

```powershell
pwsh -NoProfile -File tools\bootstrap_dev.ps1
```

這只驗證維護骨架。產品完整執行與功能測試見 [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)。

## 提交方式

本 fork 由維護者直接推 `main`，不開短期分支。改完先跑上面的 Windows gate；開 PR 時 target 必須是 `SanHsien/Skill_Seekers` 的 `main`，嚴禁指向 upstream。

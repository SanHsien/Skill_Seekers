# GEMINI.md

請先完整閱讀並遵守 [`AGENTS.md`](AGENTS.md)。本檔只補充 Gemini / Antigravity 的最小入口：

- 這是保留上游歷史的 fork；不要移除 `upstream`、原作者或 MIT License 授權標示。
- 核心程式在 `src/`，以上游為準。
- 提交前跑 `pwsh -NoProfile -File tools\dev_check.ps1`。不要把 gate 改成完整產品依賴安裝。
- 測試檔案、使用者專有文件、`.env` 一律不可提交。
- 使用繁體中文，先講結論再講細節，直接交付可驗證結果。
- PR、push、release 一律指向 `SanHsien/Skill_Seekers`，嚴禁未經當次許可打向 `yusufkaraaslan/Skill_Seekers`。

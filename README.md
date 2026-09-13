# Skill Seekers（SanHsien 維護 fork）

<div align="center">

[![CI](https://github.com/SanHsien/Skill_Seekers/actions/workflows/ci.yml/badge.svg)](https://github.com/SanHsien/Skill_Seekers/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

<br>

**開源 AI Agent 技能與知識庫轉換層**

專為想幫 AI 擴充專業知識的開發者打造的開源工具，將文件網站、GitHub 程式碼庫和 PDF 文件轉換為 Claude AI 技能。

[功能特色](#功能特色) · [快速開始](#快速開始) · [本機開發與驗收](#本機開發與驗收) · [Fork 維護說明](FORK.md) · [English](README.en.md)

</div>

本專案 fork 自 [`yusufkaraaslan/Skill_Seekers`](https://github.com/yusufkaraaslan/Skill_Seekers)，沿用 MIT License。主要定位為 **Windows-first 維護型 fork**，提供可重現的 Windows 11 原生開發環境門禁、CI 工作流程與逐筆審查的上游變更追蹤。上游原版英文說明請見 [`README.en.md`](README.en.md)，fork 維護取捨與差異清單見 [`FORK.md`](FORK.md)。

---

## 功能特色

- **18 種常見數據來源輸入**：包含官方文件網址、各類 GitHub 程式碼倉庫、PDF 文件、影片字幕、群聊紀錄等，皆可直接轉為結構化知識。
- **智慧架構掃描**：內建智慧掃描功能，可自動識別專案技術棧架構並生成對應框架設定。
- **一鍵打包至 22 個平台**：全面適配 Claude Code、Cursor、RAG 向量資料庫與各主流 LLM 開發平台。
- **豐富的 MCP 生態**：內建 40 個 MCP 工具供 AI Agent 隨時調用。
- **快速安裝**：支援透過 pip 指令快速完成本機安裝與環境配置。

---

## 快速開始

### 1. 安裝套件

```powershell
pip install skill-seekers
```

或由本專案源碼安裝：

```powershell
pip install -e .
```

### 2. 常用指令

```powershell
# 從官方文件網站建立技能（自動偵測來源類型）
skill-seekers create https://docs.react.dev --name react

# 從 GitHub 程式碼倉庫建立技能
skill-seekers create microsoft/TypeScript --name typescript

# 從本機 PDF 檔案建立技能
skill-seekers create ./documentation.pdf --name mydocs

# 智慧掃描本機專案架構
skill-seekers scan .

# 健康診斷檢查
skill-seekers doctor

# 打包技能
skill-seekers package output/react/
```

---

## 本機開發與驗收（Windows 11 原生）

本 fork 專注於 Windows 11 原生環境的穩定性與一鍵門禁：

```powershell
# 一鍵初始化虛擬環境與安裝維護依賴
pwsh -NoProfile -File tools\bootstrap_dev.ps1

# 執行 Windows 原生開發驗收門禁（編譯 + Ruff + 契約測試 + 連結檢查）
pwsh -NoProfile -File tools\dev_check.ps1

# 產品冒煙測試
pwsh -NoProfile -File tools\test_product.ps1
```

詳細開發規範請參考 [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)。

---

## 授權與維護宣告

- 本專案原始程式碼版權歸原作者 Yusuf Karaaslan 及所有貢獻者所有，採用 [`LICENSE`](LICENSE)（MIT License）。
- 本 fork 維護資訊請見 [`FORK.md`](FORK.md)、著作權宣告請見 [`NOTICE.md`](NOTICE.md)。
- 上游版本基準與決策記錄請見 [`docs/UPSTREAM.md`](docs/UPSTREAM.md) 與 [`docs/DECISIONS.md`](docs/DECISIONS.md)。

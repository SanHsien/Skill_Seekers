# 開發環境

維護者與 AI 接手用的開發文件。產品使用方式在 [`README.md`](../README.md)；上游同步在 [`UPSTREAM.md`](UPSTREAM.md)；決策在 [`DECISIONS.md`](DECISIONS.md)。

## 架構

```text
src/
  └── skill_seekers/
        ├── cli/               命令列入口、抓取器、打包與安裝邏輯
        ├── mcp/               40 個 MCP 工具與伺服器實作
        ├── services/          核心服務模組
        ├── sync/              配置同步
        ├── workflows/         技能增強工作流程預設
        └── benchmark/         效能評測套件
tools/                         fork 維護工具（Windows gate、上游檢查、相對連結檢查、依賴新鮮度）
  └── tests/                   維護契約測試
docs/                          fork 維護與治理文件
.github/
  └── workflows/               CI、安全掃描、上游追蹤與新鮮度排程
```

## 本機開發（Windows 11 原生）

### 維護骨架（必跑）

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements-dev.txt
$env:PYTHONUTF8 = "1"
pwsh -NoProfile -File tools\dev_check.ps1
```

等價一鍵指令：

```powershell
pwsh -NoProfile -File tools\bootstrap_dev.ps1
```

### 完整產品依賴安裝（選用）

若需在本機直接運行完整 CLI 爬蟲或伺服器：

```powershell
pwsh -NoProfile -File tools\bootstrap_dev.ps1 -All
```

### 產品冒煙測試

```powershell
pwsh -NoProfile -File tools\test_product.ps1
```

### 單獨執行維護工具

```powershell
# 檢查 Markdown 相對連結
python tools\check_links.py

# 檢查上游 commit、PR 與 issue 水位
python tools\check_upstream_updates.py

# 檢查依賴新鮮度
python tools\check_dependency_freshness.py
```

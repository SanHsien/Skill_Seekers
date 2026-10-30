# 上游維護

## Remote

- Fork：`origin` → `https://github.com/SanHsien/Skill_Seekers.git`（預設分支 `main`）
- 原作者：`upstream` → `https://github.com/yusufkaraaslan/Skill_Seekers.git`
- 追蹤分支：`main`

## 上游分支角色與追蹤維護政策

### 1. 分支角色比對與現有裁決

- **上游 `main`（穩定發布線）**：
  原作者以 `main` 作為對外正式發布（Release）基準。每個發布版本均於 `main` 建立 semver 標籤（如 `v3.9.1` 指向 `c333a37`、`v3.10.0` 指向 `d26c2e3`），包含經完整測試與發布門禁驗證之穩定程式碼。
- **上游 `development`（日常協作線 / GitHub 預設分支）**：
  原作者在 GitHub 將 `development` 設為預設分支，作為日常 Pull Requests、新功能整合與協作開發之集線。發版後立即推進開發版本號（如 `3.11.0.dev0`）。
- **現有裁決對齊**：
  本 fork 依據 [維護決策](DECISIONS.md)（2026-09-12、2026-10-24）確立以穩定版本 `upstream/main` 為追蹤基線，2026-10-24 整批採用 `main` 累計 74 commits 至 `d26c2e3`（v3.10.0）。追蹤分支記錄於 `tools/upstream_baseline.json`（`"branch": "main"`）。

### 2. 追蹤路線選擇權衡

| 方案 | 優點 | 代價與維護成本 | 結論 |
| --- | --- | --- | --- |
| **選項 A：維持追蹤 release 線（`upstream/main`）**<br>*(本 fork 現行政策)* | 基線穩定，僅在正式發布時審查與吸收完整功能；避免承接開發中未定案架構、半成品或中途破壞性變更；與 Windows-first 維護目標一致。 | 無法第一時間隨 commit 水位同步最新實驗改動；需仰賴每週 PR / Issue 水位監控發現尚未釋出的關鍵修復。 | **維持採用**。符合維護型 fork 的長期穩定原則。 |
| **選項 B：切換為追蹤日常開發線（`upstream/development`）** | 可同步上游最前線 commit 與實驗功能。 | 上游開發線隨時可能引入 `dev0` 暫存版本號、未固化的版本號與鎖檔變更（例：`598df68` 改了 `uv.lock`），維護成本顯著增加。 | 暫不採用。僅在上游長期停更正式版且開發線有重大核心重構時由維護者裁決。 |

### 3. 切換追蹤線的硬閘門要求

嚴禁僅為消弭排程檢查警示或簡化維護而直接修改 `tools/upstream_baseline.json` 中的 `branch` 與 `reviewed_through`（嚴禁「改水位求綠燈」）。若未來評估切換追蹤線，必須遵守以下閘門：
1. **先審差異**：必須先執行 `gh api repos/yusufkaraaslan/Skill_Seekers/compare/main...development`，完整審閱 `development` 領先 `main` 的所有 commits 與檔案變更。
2. **評估衝擊**：核對版本號變更、依賴鎖檔、Windows 門禁、API 邊界與既有裁決（如 Python 3.11+ 最低版本、路徑安全守衛）。
3. **決策記錄**：在 [維護決策](DECISIONS.md) 記載切換理由與審查細節，完成本機完整 gate 驗證後，方可推進 baseline。

### 4. 2026-10-30 上游差異比對與政策結論

- **比對指令**：`gh api repos/yusufkaraaslan/Skill_Seekers/compare/main...development`
- **比對結果**：狀態為 `ahead`（`ahead_by: 2`，`behind_by: 0`）。
- **領先 commits 審查**：
  1. `598df68` (`chore: open the 3.11.0 dev cycle`)：修改 `CHANGELOG.md`、`CLAUDE.md`、`pyproject.toml`、`src/skill_seekers/_version.py`、`uv.lock`，將版本號標記為 `3.11.0.dev0`。
  2. `5b5d8df` (`Merge main (release gate fix) into development`)：將 `main` 上的 release gate fix（`d26c2e3`）回併至 development。
- **審查結論**：`development` 目前領先 `main` 的 2 個 commits 僅屬新週期版本號宣告與反向 merge，無任何業務邏輯或安全修復。引進 `3.11.0.dev0` 反而會干擾本 fork 穩定的鎖檔與版本機制。
- **政策裁決**：本 fork **維持追蹤 `upstream/main`** 作為基準線，不切換至 `development`；未合併至 release 的個別重要修復繼續透過每週 PR/Issue 清冊獨立審查。

## 檢查新提交

```powershell
git fetch upstream main
python tools\check_upstream_updates.py --strict
```

工具以 `tools/upstream_baseline.json` 的 `reviewed_through` 為起點，列出所有未審查提交、PR 與 Issues。
有新變更或檢查失敗時，`--strict` 回傳非零；排程 workflow 也會因此明確亮紅燈提醒。

CI 沒有 `upstream` remote，所以 baseline 的 `repo` 寫完整 clone URL，不要寫遠端短名。

## 審查清冊

每次只做一次批次審查：

1. 讀 commit 主旨與變更檔案（open PR 必須讀 diff，禁止只憑標題結案）。
2. 判斷是否與繁中 README、Windows gate、發佈閘門或測試衝突。
3. 可直接同步的提交用 merge；只需要部分修正時 cherry-pick 或最小重做。
4. 跑 `pwsh -NoProfile -File tools\dev_check.ps1`。
5. 在 `docs/DECISIONS.md` 記錄採用／略過理由。
6. 驗證完成後才把 baseline 推進到已審查的完整 40 字元 SHA 與更新 PR/Issue 水位。

Baseline 代表「已審查」，不代表「全部已合併」。

## 2026-09-12：fork 起點

本 fork 自上游 `main` `c333a379bfb43f42eb605fd575be955762a9fa7b`
（`Merge branch 'development' into main — release v3.9.1`）建立。
此 SHA 設為第一個 `reviewed_through`（短 SHA 為 `c333a37`）。
之後的上游 commit 才需要進入審查清冊。
